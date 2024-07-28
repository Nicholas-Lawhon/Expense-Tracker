from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)

    transactions = relationship("Transaction", back_populates="category")
    budget = relationship("Budget", back_populates="category")
