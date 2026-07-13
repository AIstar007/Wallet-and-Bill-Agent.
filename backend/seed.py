"""
Seed demo data — idempotent, safe to call on every app startup. Creates one
demo account with a plan, a bill, and usage history if the DB is empty.

Not a migrations tool (no Alembic here — deliberate scope cut for a
hackathon scaffold). For a real deployment you'd want proper migrations
instead of create_all() + seed-on-startup.
"""
from datetime import date

from sqlalchemy.orm import Session

from backend.models import Base, Plan, Account, Bill, UsageRecord

PLAN_CATALOG = [
    {"name": "Unlimited 5G", "monthly_price": 599, "data_gb": 100, "description": "Unlimited calls + 100GB data"},
    {"name": "Smart Saver", "monthly_price": 399, "data_gb": 40, "description": "Unlimited calls + 40GB data, budget friendly"},
    {"name": "Family Max", "monthly_price": 999, "data_gb": 300, "description": "Unlimited calls + 300GB shared data, up to 4 lines"},
    {"name": "Basic Lite", "monthly_price": 249, "data_gb": 10, "description": "Cheapest plan, calls only, minimal 10GB data for light users"},
    {"name": "Business Pro", "monthly_price": 1499, "data_gb": 500, "description": "Priority network access, 500GB data, international roaming included"},
]


def seed(engine, session: Session):
    Base.metadata.create_all(bind=engine)

    if session.query(Plan).count() > 0:
        return  # already seeded

    plans = [Plan(**p) for p in PLAN_CATALOG]
    session.add_all(plans)
    session.commit()

    account = Account(customer_name="Demo Customer", plan_id=plans[0].id)
    session.add(account)
    session.commit()

    bill = Bill(
        account_id=account.id,
        period_start=date(2026, 6, 1),
        period_end=date(2026, 6, 30),
        amount=799.0,
        breakdown_json='{"plan_charge": 599, "data_overage": 150, "device_installment": 50}',
    )
    session.add(bill)

    usage = [
        UsageRecord(account_id=account.id, date=date(2026, 6, 1), data_used_mb=1200, minutes_used=45),
        UsageRecord(account_id=account.id, date=date(2026, 6, 15), data_used_mb=3400, minutes_used=20),
    ]
    session.add_all(usage)
    session.commit()
