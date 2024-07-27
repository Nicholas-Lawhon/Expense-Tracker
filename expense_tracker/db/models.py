from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()


class IntervalType(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    BI_WEEKLY = "bi-weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi-annually"
    ANNUALLY = "yearly"


class TransactionType(enum.Enum):
    EXPENSE = "expense"
    RECURRING_EXPENSE = "recurring_expense"
    INCOME = "income"
    TRANSFER = "transfer"


class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)  # Added length specification
    balance = Column(Float, default=0.0)

    transactions = relationship("Transaction", back_populates="account")
    recurring_expenses = relationship("RecurringExpense", back_populates="account")


class Budget(Base):
    __tablename__ = 'budgets'

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    amount = Column(Float, default=0.0)
    start_date = Column(Date)
    end_date = Column(Date)

    category = relationship("Category", back_populates="budget")


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)  # Added length specification
    description = Column(String(1000))  # Added length specification

    transactions = relationship("Transaction", back_populates="category")
    budget = relationship("Budget", back_populates="category")
    recurring_expenses = relationship("RecurringExpense", back_populates="category")


class RecurringExpense(Base):
    __tablename__ = 'recurring_expenses'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)  # Added length specification
    amount = Column(Float, nullable=False)
    interval = Column(Enum(IntervalType), nullable=False)
    billing_date = Column(Date, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    account_id = Column(Integer, ForeignKey('accounts.id'))
    description = Column(String(1000))  # Added length specification

    category = relationship("Category", back_populates="recurring_expenses")
    account = relationship("Account", back_populates="recurring_expenses")


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    name = Column(String(255), nullable=False)  # Added length specification
    amount = Column(Float, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String(1000))  # Added length specification

    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
