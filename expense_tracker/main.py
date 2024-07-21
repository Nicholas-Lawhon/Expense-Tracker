from expense_tracker.db import get_db_engine, Transaction, create_tables
from expense_tracker.utils.logger import setup_logger

"""
This is the main entry point for the expense tracker application.

It sets up the database and initializes the main application logic.
"""

logger = setup_logger('main', 'main.log')

if __name__ == "__main__":
    try:
        engine = create_tables()
        # Your main application logic here
    except Exception as e:
        logger.error(f"An error occurred in main: {e}")

# General Outline
# DB Tables: Transactions (Manual & Automatic), Monthly Expenses, Accounts, Categories, Budget, Goals (optional, can add later).