from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()


class IntervalType(enum.Enum):
    ONCE = "ONCE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    BI_WEEKLY = "BI_WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    SEMI_ANNUALLY = "SEMI_ANNUALLY"
    ANNUALLY = "YEARLY"


class TransactionType(enum.Enum):
    EXPENSE = "EXPENSE"
    INCOME = "INCOME"
    TRANSFER = "TRANSFER"


class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    balance = Column(Float, default=0.0, nullable=False)

    transactions = relationship("Transaction", back_populates="account")


class Budget(Base):
    __tablename__ = 'budgets'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    amount = Column(Float, default=0.0, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    category = relationship("Category", back_populates="budget")


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)

    transactions = relationship("Transaction", back_populates="category")
    budget = relationship("Budget", back_populates="category")


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    date = Column(Date, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    interval = Column('interval', Enum(IntervalType), nullable=False, default=IntervalType.ONCE)
    billing_date = Column(Date, nullable=True)
    description = Column(String(1000), nullable=True)

    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
