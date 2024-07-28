from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from .base import Base


class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    balance = Column(Float, default=0.0, nullable=False)

    transactions = relationship("Transaction", back_populates="account")
