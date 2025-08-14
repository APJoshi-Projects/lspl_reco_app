import os, json
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import select, or_
from db import SessionLocal
from models import Product, Ticket, RnDRecord, TrialRecord, ComplaintRecord
from prompts import SYSTEM_PROMPT, USER_TEMPLATE

# Embeddings: default to sentence-transformers
USE_OPENAI_EMB = os.getenv("EMBEDDINGS_PROVIDER", "").lower() == "openai"
EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# LangChain LLM (OpenAI-compatible, e.g., Grok via base_url)
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore

if USE_OPENAI_EMB:
    from langchain_openai import OpenAIEmbeddings
else:
    from langchain_community.embeddings import HuggingFaceEmbeddings

class InputSchema(BaseModel):
    # Core sales inputs:
    timestamp: Optional[str] = None
    email: Optional[str] = None
    required_by: Optional[str] = None
    requirement_type: Optional[str] = None
    division: str
    category: str
    requirement_details: Optional[str] = None
    priority: Optional[str] = None
    customer_name: Optional[str] = None
    remark: Optional[str] = None
    ticket_type: Optional[str] = None
    target_date: Optional[str] = None

    # Category-specific (examples; free text accepted; UI will populate many fields)
    params: Dict[str, Any] = Field(default_factory=dict)

class Recommender:
    def __init__(self):
        self.db = SessionLocal
        self._vec = None
        self._emb = None
        self._llm = None

    def _get_embeddings(self):
        if self._emb:
            return self._emb
        if USE_OPENAI_EMB:
            self._emb = OpenAIEmbeddings(model=EMBEDDINGS_MODEL, openai_api_base=os.getenv("LLM_API_BASE") or None, openai_api_key=os.getenv("LLM_API_KEY"))
        else:
            self._emb = HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL)
        return self._emb

    def _get_llm(self):
        if self._llm:
            return self._llm
        self._llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_API_BASE") or None,
            temperature=0.1,
        )
        return self._llm

    def _ensure_vector_index(self):
        if self._vec:
            return self._vec
        emb = self._get_embeddings()
        # Build docs from ticket history
        db = self.db()
        try:
            tickets = db.query(Ticket).all()
        finally:
            db.close()
        docs = []
        metadatas = []
        for t in tickets:
            text = f"""Ticket {t.ticket_id or t.id}
Division={t.division} Category={t.category}
Details={t.requirement_details}
Proposed={t.proposed_grade} Reason={t.proposed_reason}
Customer={t.customer_name} Priority={t.priority}
"""
            docs.append(text)
            metadatas.append({"id": t.id, "proposed": t.proposed_grade or ""})
        if not docs:
            # initialize empty index
            self._vec = FAISS.from_texts(["seed"], emb, metadatas=[{}])
            return self._vec
        self._vec = FAISS.from_texts(docs, emb, metadatas=metadatas)
        return self._vec

    def _summarize_input(self, data: InputSchema) -> str:
        parts = [
            f"Division={data.division}",
            f"Category={data.category}",
            f"RequirementType={data.requirement_type}",
            f"Priority={data.priority}",
            f"Customer={data.customer_name}",
            f"Details={data.requirement_details}",
            f"Params={json.dumps(data.params)[:800]}",
        ]
        return "\n".join([p for p in parts if p and not p.endswith("=None")])

    def _fetch_candidates(self, division: str, category: str) -> List[Product]:
        db = self.db()
        try:
            q = db.query(Product).filter(
                or_(Product.division==division, Product.division==None),
                or_(Product.category==category, Product.category==None)
            )
            return q.all()
        finally:
            db.close()

    def _evidence_blocks(self, data: InputSchema, candidates: List[Product]):
        # R&D checks, trials, complaints gathered as text summaries
        db = self.db()
        try:
            rnd_map = {}
            for c in candidates:
                recs = db.query(RnDRecord).filter(RnDRecord.lspl_grade==c.lspl_grade).all()
                rnd_map[c.lspl_grade] = "; ".join([f"{r.spec_summary} | Constraints: {r.constraints or '-'}" for r in recs]) or "-"

            trial_map = {}
            for c in candidates:
                rows = db.query(TrialRecord).filter(TrialRecord.lspl_grade==c.lspl_grade).all()
                # prioritize same customer if provided
                same_customer = [r for r in rows if data.customer_name and r.customer_name == data.customer_name]
                pref = same_customer or rows
                trial_map[c.lspl_grade] = "; ".join([f"{r.customer_name}:{r.outcome} ({(r.notes or '')[:80]})" for r in pref[:3]]) or "-"

            cmpl_map = {}
            for c in candidates:
                rows = db.query(ComplaintRecord).filter(ComplaintRecord.lspl_grade==c.lspl_grade).all()
                cmpl_map[c.lspl_grade] = "; ".join([f"{r.customer_name}:{r.severity}({(r.issue or '')[:60]})" for r in rows[:3]]) or "-"

            return rnd_map, trial_map, cmpl_map
        finally:
            db.close()

    def recommend(self, data: InputSchema) -> Dict[str, Any]:
        # Nearest tickets
        vec = self._ensure_vector_index()
        query = self._summarize_input(data)
        nearest = vec.similarity_search(query, k=5) if vec else []

        nearest_text = "\n---\n".join([d.page_content for d in nearest]) if nearest else "-"

        # Candidate products
        candidates = self._fetch_candidates(data.division, data.category)
        if not candidates:
            candidates = self._fetch_candidates(data.division, None) + self._fetch_candidates(None, data.category)

        rnd_map, trial_map, cmpl_map = self._evidence_blocks(data, candidates)

        candidates_summary = []
        for c in candidates[:10]:
            spec = f"Grade={c.lspl_grade}; Proc={c.compatible_process}; Metal={c.metal}; T={c.temp_min_c}-{c.temp_max_c}C; Notes={(c.notes or '')[:80]}"
            spec += f" | Trials: {trial_map.get(c.lspl_grade,'-')} | Complaints: {cmpl_map.get(c.lspl_grade,'-')}"
            candidates_summary.append(spec)

        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("user", USER_TEMPLATE)
        ]).format_messages(
            input_summary=self._summarize_input(data),
            candidates_summary="\n".join(candidates_summary) or "-",
            nearest_tickets=nearest_text,
            rnd_checks=json.dumps(rnd_map, indent=2),
            trial_signals=json.dumps(trial_map, indent=2),
            complaint_signals=json.dumps(cmpl_map, indent=2),
        )

        llm = self._get_llm()
        parser = JsonOutputParser()
        raw = llm.invoke(prompt)
        try:
            parsed = parser.parse(raw.content)
        except Exception:
            parsed = {"grade": "TBD", "reason": raw.content[:500], "notes": ""}

        # Return structured payload matching required output columns
        return {
            "LSPL proposed Grade": parsed.get("grade"),
            "Reason for proposing the LSPL Grade": parsed.get("reason"),
            "Notes": parsed.get("notes"),
            "debug": {
                "nearest_count": len(nearest),
                "candidate_count": len(candidates)
            }
        }
