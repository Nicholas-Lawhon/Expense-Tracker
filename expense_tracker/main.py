from expense_tracker.db import get_db_engine, create_tables, drop_tables
from expense_tracker.utils.logger import setup_logger
from expense_tracker.cli import CLI
from sqlalchemy import inspect

logger = setup_logger('main', 'main.log')


def check_tables(engine):
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    logger.info(f"Existing tables: {existing_tables}")
    return existing_tables


if __name__ == "__main__":
    try:
        engine = get_db_engine()
        existing_tables = check_tables(engine)

        if not existing_tables:
            logger.info("No tables found. Creating tables...")
            create_tables(engine)
            existing_tables = check_tables(engine)

        logger.info("Database setup complete.")

        # Check if all expected tables are created
        expected_tables = ['accounts', 'budgets', 'categories', 'recurring_expenses', 'transactions']
        missing_tables = set(expected_tables) - set(existing_tables)

        if missing_tables:
            logger.warning(f"Some tables are missing: {missing_tables}")
        else:
            logger.info("All expected tables are present.")

        # Initialize and run the CLI
        cli = CLI()
        cli.run()
    except Exception as e:
        logger.error(f"An error occurred in main: {e}")
