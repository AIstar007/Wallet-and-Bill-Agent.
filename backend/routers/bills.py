"""
Bill / usage / plan REST endpoints — backed by the real database, not mock
dicts. Kept separate from the chat/AI layer: the chat agent calls these as
tools rather than duplicating data-access logic, so the same endpoints
serve the dashboard, the agent, and any future client identically.
"""
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.models import Account, Bill, UsageRecord, Plan

router = APIRouter()


@router.get("/bills/{account_id}")
def get_bill(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if account is None:
        raise HTTPException(status_code=404, detail=f"No account found with id {account_id}")

    bill = (
        db.query(Bill)
        .filter(Bill.account_id == account_id)
        .order_by(Bill.period_end.desc())
        .first()
    )
    if bill is None:
        raise HTTPException(status_code=404, detail=f"No bill found for account {account_id}")

    return {
        "account_id": bill.account_id,
        "period_start": str(bill.period_start),
        "period_end": str(bill.period_end),
        "amount": bill.amount,
        "breakdown": json.loads(bill.breakdown_json or "{}"),
    }


@router.get("/usage/{account_id}")
def get_usage(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if account is None:
        raise HTTPException(status_code=404, detail=f"No account found with id {account_id}")

    records = db.query(UsageRecord).filter(UsageRecord.account_id == account_id).order_by(UsageRecord.date).all()
    return [
        {"date": str(r.date), "data_used_mb": r.data_used_mb, "minutes_used": r.minutes_used}
        for r in records
    ]


@router.get("/plans")
def list_plans(db: Session = Depends(get_db)):
    plans = db.query(Plan).all()
    return [
        {"id": p.id, "name": p.name, "monthly_price": p.monthly_price, "data_gb": p.data_gb, "description": p.description}
        for p in plans
    ]
