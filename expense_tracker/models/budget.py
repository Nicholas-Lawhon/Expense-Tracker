from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Budget(Base):
    __tablename__ = 'budgets'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    amount = Column(Float, default=0.0, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    category = relationship("Category", back_populates="budget")
