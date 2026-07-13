import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite by default so `uvicorn main:app --reload` works with zero setup.
# Set DATABASE_URL to a Postgres connection string for production.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./wallet_bill_agent.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
