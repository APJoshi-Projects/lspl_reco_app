# Minimal MCP server exposing read-only SQL tools for the LLM
import os, json, asyncio
from db import SessionLocal
from models import Ticket, Product, TrialRecord, ComplaintRecord, RnDRecord

from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("lspl-mcp")

@server.list_tools()
async def list_tools():
    return [
        Tool(name="sql_recent_tickets", description="Return last N tickets", inputSchema={"type":"object","properties":{"limit":{"type":"number","default":10}},"required":[]}),
        Tool(name="sql_product_by_category", description="List products by division/category", inputSchema={"type":"object","properties":{"division":{"type":"string"},"category":{"type":"string"}},"required":[]}),
        Tool(name="sql_trials_by_grade", description="Trials for a given LSPL grade", inputSchema={"type":"object","properties":{"grade":{"type":"string"}},"required":["grade"]}),
        Tool(name="sql_complaints_by_grade", description="Complaints for a given LSPL grade", inputSchema={"type":"object","properties":{"grade":{"type":"string"}},"required":["grade"]}),
        Tool(name="sql_rnd_by_grade", description="R&D records for a given LSPL grade", inputSchema={"type":"object","properties":{"grade":{"type":"string"}},"required":["grade"]})
    ]

@server.call_tool()
async def call_tool(name, arguments):
    db = SessionLocal()
    try:
        if name == "sql_recent_tickets":
            lim = int(arguments.get("limit", 10))
            rows = db.query(Ticket).order_by(Ticket.id.desc()).limit(lim).all()
            return [TextContent(type="text", text=json.dumps([r.to_dict() for r in rows], indent=2))]

        if name == "sql_product_by_category":
            div = arguments.get("division")
            cat = arguments.get("category")
            q = db.query(Product)
            if div: q = q.filter(Product.division==div)
            if cat: q = q.filter(Product.category==cat)
            rows = q.limit(50).all()
            return [TextContent(type="text", text=json.dumps([{"lspl_grade":r.lspl_grade,"division":r.division,"category":r.category} for r in rows], indent=2))]

        if name == "sql_trials_by_grade":
            g = arguments["grade"]
            rows = db.query(TrialRecord).filter(TrialRecord.lspl_grade==g).all()
            return [TextContent(type="text", text=json.dumps([{"customer":r.customer_name,"outcome":r.outcome,"notes":r.notes} for r in rows], indent=2))]

        if name == "sql_complaints_by_grade":
            g = arguments["grade"]
            rows = db.query(ComplaintRecord).filter(ComplaintRecord.lspl_grade==g).all()
            return [TextContent(type="text", text=json.dumps([{"customer":r.customer_name,"severity":r.severity,"issue":r.issue} for r in rows], indent=2))]

        if name == "sql_rnd_by_grade":
            g = arguments["grade"]
            rows = db.query(RnDRecord).filter(RnDRecord.lspl_grade==g).all()
            return [TextContent(type="text", text=json.dumps([{"spec":r.spec_summary,"constraints":r.constraints} for r in rows], indent=2))]

        return [TextContent(type="text", text=json.dumps({"error":"unknown tool"}, indent=2))]
    finally:
        db.close()

async def main():
    await server.run_stdio()

if __name__ == "__main__":
    asyncio.run(main())
