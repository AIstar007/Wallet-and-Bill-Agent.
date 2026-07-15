"""
Chat endpoint — bill explanation + plan comparison, grounded in the real
DB (bill data) and real FAISS vector search (plan matching), not static
mock lists.
"""
import json
import os

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.models import Account, Bill, Plan
from backend.llm import llm_call as real_llm_call
from backend.plan_search import PlanSearchIndex

router = APIRouter()

ACTIVE_LLM_CALL = (
    real_llm_call
    if all(
        [
            os.getenv("AZURE_OPENAI_API_KEY"),
            os.getenv("AZURE_OPENAI_ENDPOINT"),
            os.getenv("AZURE_OPENAI_API_VERSION"),
            os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        ]
    )
    else None
)

SYSTEM_PROMPT = """You are a billing & plans assistant for a telecom customer.
Explain charges in plain language and compare plans ONLY using the data provided.
Never claim you've switched or refunded anything — you can only recommend, a human confirms."""

_plan_index = PlanSearchIndex()


class ChatRequest(BaseModel):
    message: str
    account_id: int = 1


class ChatResponse(BaseModel):
    answer: str
    referenced_plans: list[str]


def _plans_as_dicts(db: Session) -> list[dict]:
    return [
        {"id": p.id, "name": p.name, "monthly_price": p.monthly_price, "data_gb": p.data_gb, "description": p.description}
        for p in db.query(Plan).all()
    ]


def build_context(db: Session, account_id: int, query: str) -> tuple[str, list[str]]:
    all_plans = _plans_as_dicts(db)
    _plan_index.build(all_plans)  # cheap at this catalog size; cache/invalidate properly at real scale

    matched_ids = _plan_index.search(query, k=2)
    matched_plans = [p for p in all_plans if p["id"] in matched_ids] or all_plans

    bill_line = "No bill on file."
    bill = (
        db.query(Bill)
        .filter(Bill.account_id == account_id)
        .order_by(Bill.period_end.desc())
        .first()
    )
    if bill is not None:
        breakdown = json.loads(bill.breakdown_json or "{}")
        bill_line = f"₹{bill.amount} for {bill.period_start} to {bill.period_end} ({breakdown})"

    plans_str = "\n".join(f"- {p['name']}: ₹{p['monthly_price']}/mo, {p['data_gb']}GB" for p in matched_plans)
    context = f"Current bill: {bill_line}\n\nRelevant plans:\n{plans_str}"
    return context, [p["name"] for p in matched_plans]


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    context, referenced_plans = build_context(db, req.account_id, req.message)

    if ACTIVE_LLM_CALL is not None:
        answer = ACTIVE_LLM_CALL(SYSTEM_PROMPT, f"Context:\n{context}\n\nQuestion: {req.message}")
    else:
        answer = (
            f"[stub] Based on your current bill and {len(referenced_plans)} matched plan(s), "
            f"here's an answer to: '{req.message}'"
        )
    return ChatResponse(answer=answer, referenced_plans=referenced_plans)
