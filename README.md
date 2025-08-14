# LSPL Product Recommendation App (Flask + LangChain + MCP)

A reference implementation for recommending LSPL grades from tickets + R&D + trials + complaints.
It mixes heuristic filtering with LLM reasoning (Grok or any OpenAI-compatible endpoint) via LangChain,
and exposes your internal data safely through Model Context Protocol (MCP) tools.

## Features
- Flask API (`/api/recommend`) that accepts your sales inputs
- SQLAlchemy models for Tickets, Products, R&D specs, Trials, Complaints
- Vector search over past tickets with FAISS + Sentence-Transformers (or OpenAI-compatible embeddings)
- LangChain pipeline to synthesize a final recommendation with **structured JSON output**
- Minimal web UI in `templates/index.html`
- Example MCP server (`mcp_server.py`) exposing safe SQL read tools

## Quickstart

1) Create virtualenv and install deps
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2) Configure environment
```bash
cp .env.example .env
# edit .env with your keys and model names
```

3) Initialize the database (creates SQLite `reco.db` with demo rows)
```bash
python seed.py
```

4) Run Flask app
```bash
python app.py
# open http://127.0.0.1:5000
```

5) (Optional) Run MCP server
```bash
python mcp_server.py
```

## Notes
- Replace `LLM_API_BASE/LLM_MODEL/LLM_API_KEY` for your provider (e.g., xAI Grok) if it supports OpenAI-compatible routes.
- For production, move secrets out of `.env`, add auth, data governance, and robust validations.
