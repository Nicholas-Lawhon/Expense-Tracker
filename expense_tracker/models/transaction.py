from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .base import Base
from .enums import TransactionType, IntervalType


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

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'amount': self.amount,
            'account_id': self.account_id,
            'category_id': self.category_id,
            'date': self.date.isoformat(),
            'type': self.type.name,
            'interval': self.interval.name,
            'billing_date': self.billing_date.isoformat() if self.billing_date else None,
            'description': self.description
        }
