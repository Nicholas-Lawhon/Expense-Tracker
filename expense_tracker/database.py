import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.orm import declarative_base

# Get the directory of the current file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up one level to the project root
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
# Construct the path to the database file
db_path = os.path.join(PROJECT_ROOT, "data", "database.db")

# Look to wrap engine and table creation into functions.
db_url = f"sqlite:///{db_path}"
db_engine = create_engine(db_url)

Base = declarative_base()


# Table Definitions
class Transaction(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    description = Column(String)
    amount = Column(Float)
    date = Column(Date)
    category = Column(String)


# Table Creation
def create_tables():
    Base.metadata.create_all(db_engine)


# Only create tables if this file is ran directly
if __name__ == '__main__':
    create_tables()