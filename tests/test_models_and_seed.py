from sqlalchemy.orm import Session

from backend.db import engine, SessionLocal
from backend.models import Account, Bill, Plan
from backend.seed import seed


def test_seed_is_idempotent():
    db = SessionLocal()
    try:
        seed(engine, db)
        count_after_first = db.query(Plan).count()
        seed(engine, db)  # calling again should not duplicate
        count_after_second = db.query(Plan).count()
        assert count_after_first == count_after_second
    finally:
        db.close()


def test_seeded_account_has_bill_and_plan():
    db = SessionLocal()
    try:
        seed(engine, db)
        account = db.query(Account).filter(Account.id == 1).first()
        assert account is not None
        assert account.plan is not None

        bill = db.query(Bill).filter(Bill.account_id == account.id).first()
        assert bill is not None
        assert bill.amount > 0
    finally:
        db.close()
