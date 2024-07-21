from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from .config import DB_URL
from .models import Base
from ..utils.logger import setup_logger

"""
This module handles database connection and table creation.

It provides functions to create a database engine and initialize the database schema.
"""

# Set up logging
logger = setup_logger('database', 'database.log')

def get_db_engine():
    """
    Create and return a SQLAlchemy database engine.

    Returns:
        engine: SQLAlchemy engine object

    Raises:
        SQLAlchemyError: If there's an error creating the engine
    """
    try:
        engine = create_engine(DB_URL)
        logger.info("Database engine created successfully")
        return engine
    except SQLAlchemyError as e:
        logger.error(f"Error creating database engine: {e}")
        raise

def create_tables(engine=None):
    """
    Create all tables defined in the models.

    This function uses the Base metadata from the models to create all defined tables.

    Raises:
        SQLAlchemyError: If there's an error creating the tables
    """
    try:
        if engine is None:
            engine = get_db_engine()
        Base.metadata.create_all(engine)
        logger.info("Tables created successfully")
        return engine
    except SQLAlchemyError as e:
        logger.error(f"Error creating tables: {e}")
        raise


if __name__ == '__main__':
    try:
        create_tables()
    except Exception as e:
        logger.error(f"An error occurred: {e}")