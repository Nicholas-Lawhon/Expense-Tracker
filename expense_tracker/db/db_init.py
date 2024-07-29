from sqlalchemy import inspect
from expense_tracker.db.connection import create_tables, get_db_engine
from expense_tracker.utils.logger import setup_logger
from expense_tracker.models import Base, Account, Transaction, Budget, Category, enums


logger = setup_logger('db_init', 'db_init.log')


def init_db():
    engine = get_db_engine()
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    if not existing_tables:
        print("Creating tables...")
        create_tables(engine)
        print("Tables created successfully.")
    else:
        print("Tables already exist. No action taken.")


if __name__ == "__main__":
    init_db()
