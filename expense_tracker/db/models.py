from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship
import enum

"""
This module defines the database models using SQLAlchemy's ORM.

It currently includes a Transaction model for storing expense information.
"""

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
    """
    Contains checking, savings and credit card accounts.
    """
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    balance = Column(Float, default=0.0)

    transactions = relationship("Transaction", back_populates="account")
    recurring_expenses = relationship("RecurringExpense", back_populates="account")


class Budget(Base):
    """
    Contains information related to a user defined budget.
    """
    __tablename__ = 'budgets'

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    amount = Column(Float, default=0.0)
    start_date = Column(Date)
    end_date = Column(Date)

    category = relationship("Category", back_populates="budget")


class Category(Base):
    """
    Classifies transactions into related categories.
    """
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)

    transactions = relationship("Transaction", back_populates="category")
    budget = relationship("Budget", back_populates="category")
    recurring_expenses = relationship("RecurringExpense", back_populates="category")
    
    
class RecurringExpense(Base):
    """
    A list of monthly/yearly recurring expenses or subscriptions.
    """
    __tablename__ = 'recurring_expenses'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    interval = Column(Enum(IntervalType), nullable=False)
    billing_date = Column(Date, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    account_id = Column(Integer, ForeignKey('accounts.id'))
    description = Column(String)

    category = relationship("Category", back_populates="recurring_expenses")
    account = relationship("Account", back_populates="recurring_expenses")


class Transaction(Base):
    """
    A table containing manually entered, and automatically fetched (through API) transactions.
    """
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String)

    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")