from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from expense_tracker.config import Config
from expense_tracker.models import Base
from expense_tracker.utils.logger import setup_logger

"""
This module handles database connection and table creation.

It provides functions to create a database engine and initialize the database schema.
"""

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
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
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
        if engine is None:
            engine = get_db_engine()
        logger.info("Starting table creation...")
        Base.metadata.create_all(engine)
        logger.info("Finished table creation process")
    except SQLAlchemyError as e:
        logger.error(f"Error creating tables: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during table creation: {str(e)}")
        raise


def drop_tables(engine):
    if engine is None:
        engine = get_db_engine()
    Base.metadata.drop_all(engine)
    logger.info("All tables dropped")


if __name__ == '__main__':
    try:
        create_tables()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
