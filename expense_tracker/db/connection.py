from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from expense_tracker.utils.crypto import decrypt_value
from expense_tracker.models import Base
from expense_tracker.utils.logger import setup_logger
import os
from dotenv import load_dotenv

"""
This module handles database connection and table creation.

It provides functions to create a database engine and initialize the database schema.
"""

# Set up logging
logger = setup_logger('database', 'database.log')

load_dotenv()


def get_db_url():
    encryption_key = os.getenv('ENCRYPTION_KEY').encode()
    db_password = decrypt_value(encryption_key, os.getenv('DB_PASSWORD'))
    return f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{db_password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME')}"


def get_db_engine():
    """
    Create and return a SQLAlchemy database engine.

    Returns:
        engine: SQLAlchemy engine object

    Raises:
        SQLAlchemyError: If there's an error creating the engine
    """
    try:
        engine = create_engine(get_db_url())
        logger.info("Database engine created successfully")
        return engine
    except SQLAlchemyError as e:
        logger.error(f"Error creating database engine: {e}")
        raise


def get_db_session():
    """
    Create and return a new database session.

    Returns:
      session: SQLAlchemy session object

    Raises:
      SQLAlchemyError: If there's an error creating the session
    """
    try:
        engine = get_db_engine()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return SessionLocal()
    except SQLAlchemyError as e:
        logger.error(f"Error creating database session: {e}")
        raise


def create_tables(engine=None):
    """
    Create all tables defined in the models.

    This function uses the Base metadata from the models to create all defined tables.

    Raises:
        SQLAlchemyError: If there's an error creating the tables
    """
    try:
        logger.info("Starting table creation...")
        tables = Base.metadata.sorted_tables
        for table in tables:
            try:
                logger.info(f"Attempting to create table: {table.name}")
                table.create(engine, checkfirst=True)
                logger.info(f"Successfully created table: {table.name}")
            except SQLAlchemyError as e:
                logger.error(f"Error creating table {table.name}: {str(e)}")
        logger.info("Finished table creation process")
    except Exception as e:
        logger.error(f"Unexpected error during table creation: {str(e)}")
        raise


def drop_tables(engine):
    Base.metadata.drop_all(engine)
    logger.info("All tables dropped")


if __name__ == '__main__':
    try:
        create_tables()
    except Exception as e:
        logger.error(f"An error occurred: {e}")