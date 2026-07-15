"""
Chat endpoint — bill explanation + plan comparison, grounded in the real
DB (bill data) and real FAISS vector search (plan matching), not static
mock lists.
"""

import json
import os

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.models import Bill, Plan
from backend.llm import (
    llm_call as real_llm_call,
    llm_stream as real_llm_stream,
)
from backend.plan_search import PlanSearchIndex

router = APIRouter()

ACTIVE_LLM = all(
    [
        os.getenv("AZURE_OPENAI_API_KEY"),
        os.getenv("AZURE_OPENAI_ENDPOINT"),
        os.getenv("AZURE_OPENAI_API_VERSION"),
        os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    ]
)

SYSTEM_PROMPT = """You are a billing & plans assistant for a telecom customer.

Explain charges in plain language.

Use Markdown formatting.

When comparing plans, use bullet lists or tables.

Never claim you've switched, cancelled or refunded anything.

You may only recommend actions.
"""

_plan_index = PlanSearchIndex()


class ChatRequest(BaseModel):
    message: str
    account_id: int = 1


class ChatResponse(BaseModel):
    answer: str
    referenced_plans: list[str]


def _plans_as_dicts(db: Session):
    return [
        {
            "id": p.id,
            "name": p.name,
            "monthly_price": p.monthly_price,
            "data_gb": p.data_gb,
            "description": p.description,
        }
        for p in db.query(Plan).all()
    ]


def build_context(
    db: Session,
    account_id: int,
    query: str,
):
    all_plans = _plans_as_dicts(db)

    _plan_index.build(all_plans)

    matched_ids = _plan_index.search(query, k=2)

    matched_plans = (
        [p for p in all_plans if p["id"] in matched_ids]
        or all_plans
    )

    bill_line = "No bill on file."

    bill = (
        db.query(Bill)
        .filter(Bill.account_id == account_id)
        .order_by(Bill.period_end.desc())
        .first()
    )

    if bill is not None:
        breakdown = json.loads(bill.breakdown_json or "{}")

        bill_line = (
            f"₹{bill.amount} "
            f"for {bill.period_start} "
            f"to {bill.period_end} "
            f"({breakdown})"
        )

    plans_str = "\n".join(
        f"- {p['name']}: ₹{p['monthly_price']}/month ({p['data_gb']} GB)"
        for p in matched_plans
    )

    context = (
        f"Current Bill:\n{bill_line}\n\n"
        f"Relevant Plans:\n{plans_str}"
    )

    return context, [p["name"] for p in matched_plans]


@router.post("/chat", response_model=ChatResponse)
def chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
):
    context, referenced_plans = build_context(
        db,
        req.account_id,
        req.message,
    )

    if ACTIVE_LLM:
        answer = real_llm_call(
            SYSTEM_PROMPT,
            f"Context:\n{context}\n\nQuestion:\n{req.message}",
        )
    else:
        answer = (
            f"[stub] Based on your current bill and "
            f"{len(referenced_plans)} matched plan(s), "
            f"here's an answer to '{req.message}'."
        )

    return ChatResponse(
        answer=answer,
        referenced_plans=referenced_plans,
    )


@router.post("/chat/stream")
def chat_stream(
    req: ChatRequest,
    db: Session = Depends(get_db),
):
    context, _ = build_context(
        db,
        req.account_id,
        req.message,
    )

    prompt = (
        f"Context:\n{context}\n\n"
        f"Question:\n{req.message}"
    )

    def event_stream():
        if not ACTIVE_LLM:
            yield "data: Streaming isn't available because Azure OpenAI isn't configured.\n\n"
            yield "event: done\ndata: [DONE]\n\n"
            return

        try:
            for chunk in real_llm_stream(
                SYSTEM_PROMPT,
                prompt,
            ):
                if chunk:
                    yield f"data: {chunk}\n\n"

            yield "event: done\ndata: [DONE]\n\n"

        except Exception as exc:
            yield f"event: error\ndata: {str(exc)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
