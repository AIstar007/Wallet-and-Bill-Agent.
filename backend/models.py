from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    monthly_price = Column(Float, nullable=False)
    data_gb = Column(Integer, nullable=False)
    description = Column(String, default="")


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    customer_name = Column(String, nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"))
    plan = relationship("Plan")


class Bill(Base):
    __tablename__ = "bills"
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    breakdown_json = Column(String, default="{}")  # simplified: JSON-as-text for scaffold
    account = relationship("Account")


class UsageRecord(Base):
    __tablename__ = "usage_records"
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    date = Column(Date, nullable=False)
    data_used_mb = Column(Float, default=0)
    minutes_used = Column(Float, default=0)
