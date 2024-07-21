from sqlalchemy.orm import sessionmaker, Session, DeclarativeMeta
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_

from typing import Type, List, Optional, Generator, Tuple, Any

from .connection import get_db_engine
from ..utils.logger import setup_logger

engine = get_db_engine()
SessionLocal = sessionmaker(bind=engine)

logger = setup_logger('database_operations', 'database_operations.log')


def get_db() -> Generator[Session, None, None]:
    """
    Create a new database session and handle its lifecycle.

    Yields:
        Session: A SQLAlchemy database session.

    Note:
        This function is designed to be used as a dependency in web frameworks
        like FastAPI, ensuring proper session management.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class BaseOperations:
    """
    Provides a set of basic database operations for SQLAlchemy models.

    This class includes static methods for creating, reading, updating, and deleting instances
    of SQLAlchemy model classes. It is designed to be used with a SQLAlchemy `Session` object
    to perform operations within a database session.

    Methods:
        create(db, model_class, **kwargs) -> DeclarativeMeta:
            Creates a new instance of the given model class with the provided attributes.

        read(db, model_class, instance_id) -> Optional[DeclarativeMeta]:
            Retrieves an instance of the given model class by its ID.

        update(db, model_class, instance_id, **kwargs) -> Optional[DeclarativeMeta]:
            Updates an existing instance of the given model class by its ID with the provided attributes.

        delete(db, model_class, instance_id) -> bool:
            Deletes an instance of the given model class by its ID.

        get_all(db, model_class, page, per_page) -> Tuple[List[DeclarativeMeta], int]:
            Retrieves all instances of the given model class with pagination.

        query(db, model_class, page, per_page, **filters) -> Tuple[List[DeclarativeMeta], int]:
            Queries instances of the given model class with optional filters and pagination.
    """
    @staticmethod
    def create(
        db: Session,
        model_class: Type[DeclarativeMeta],
        **kwargs: Any,
    ) -> DeclarativeMeta:
        """
        Create a new instance of the given model class.

        Args:
            db (Session): The database session.
            model_class (Type[DeclarativeMeta]): The SQLAlchemy model class.
            **kwargs: Attributes for the new instance.

        Returns:
            DeclarativeMeta: The newly created instance.
        """
        try:
            new_instance = model_class(**kwargs)
            db.add(new_instance)
            db.commit()
            db.refresh(new_instance)
            logger.info(f"Created new {model_class.__name__}: ID {new_instance.id}, Attributes: {kwargs}")
            return new_instance
        except SQLAlchemyError as e:
            logger.error(f"Database error creating {model_class.__name__}: {e}", exc_info=True)
            db.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating {model_class.__name__}: {e}", exc_info=True)
            db.rollback()
            raise

    @staticmethod
    def read(
        db: Session,
        model_class: Type[DeclarativeMeta],
        instance_id: int,
    ) -> Optional[DeclarativeMeta]:
        """
        Read an instance of the given model class by its ID.

        Args:
            db (Session): The database session.
            model_class (Type[DeclarativeMeta]): The SQLAlchemy model class.
            instance_id (int): The ID of the instance to read.

        Returns:
            Optional[DeclarativeMeta]: The instance if found, None otherwise.
        """
        try:
            instance = db.query(model_class).filter(model_class.id == instance_id).first()
            if instance:
                logger.info(f"Retrieved {model_class.__name__}: ID {instance_id}, Attributes: {instance.__dict__}")
                return instance
            else:
                logger.warning(f"{model_class.__name__} not found: ID {instance_id}")
                return None
        except SQLAlchemyError as e:
            logger.error(f"Database error reading {model_class.__name__} ID {instance_id}: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error reading {model_class.__name__} ID {instance_id}: {e}", exc_info=True)
            raise

    @staticmethod
    def update(
        db: Session,
        model_class: Type[DeclarativeMeta],
        instance_id: int,
        **kwargs: Any,
    ) -> Optional[DeclarativeMeta]:
        """
        Update an instance of the given model class by its ID.

        Args:
            db (Session): The database session.
            model_class (Type[DeclarativeMeta]): The SQLAlchemy model class.
            instance_id (int): The ID of the instance to update.
            **kwargs: Attributes to update.

        Returns:
            Optional[DeclarativeMeta]: The updated instance if found, None otherwise.
        """
        try:
            instance = db.query(model_class).filter(model_class.id == instance_id).first()
            if instance:
                for key, value in kwargs.items():
                    setattr(instance, key, value)
                db.commit()
                logger.info(
                    f"Updated {model_class.__name__}: ID {instance_id}. Fields updated: {', '.join(kwargs.keys())}, New values: {kwargs}")
                return instance
            else:
                logger.warning(f"{model_class.__name__} not found for update: ID {instance_id}")
                return None
        except SQLAlchemyError as e:
            logger.error(f"Database error updating {model_class.__name__} ID {instance_id}: {e}", exc_info=True)
            db.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating {model_class.__name__} ID {instance_id}: {e}", exc_info=True)
            db.rollback()
            raise

    @staticmethod
    def delete(
        db: Session,
        model_class: Type[DeclarativeMeta],
        instance_id: int,
    ) -> bool:
        """
        Delete an instance of the given model class by its ID.

        Args:
            db (Session): The database session.
            model_class (Type[DeclarativeMeta]): The SQLAlchemy model class.
            instance_id (int): The ID of the instance to delete.

        Returns:
            bool: True if the instance was deleted, False if not found.
        """
        try:
            instance = db.query(model_class).filter(model_class.id == instance_id).first()
            if instance:
                db.delete(instance)
                db.commit()
                logger.info(f"Deleted {model_class.__name__}: ID {instance_id}")
                return True
            else:
                logger.warning(f"{model_class.__name__} not found for deletion: ID {instance_id}")
                return False
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting {model_class.__name__}: {e}", exc_info=True)
            db.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting {model_class.__name__}: {e}", exc_info=True)
            db.rollback()
            raise

    @staticmethod
    def get_all(
        db: Session,
        model_class: Type[DeclarativeMeta],
        page: int = 1,
        per_page: int = 10,
    ) -> Tuple[List[DeclarativeMeta], int]:
        """
        Retrieve all instances of the given model class with pagination.

        Args:
            db (Session): The database session.
            model_class (Type[DeclarativeMeta]): The SQLAlchemy model class.
            page (int): The page number (1-indexed).
            per_page (int): The number of items per page.

        Returns:
            Tuple[List[DeclarativeMeta], int]: A tuple containing the list of instances and the total count.
        """
        try:
            query = db.query(model_class)
            total = query.count()
            instances = query.offset((page - 1) * per_page).limit(per_page).all()
            logger.info(
                f"Retrieved {model_class.__name__} instances. Page {page}, {len(instances)} items. Total: {total}")
            return instances, total
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving {model_class.__name__} instances: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving {model_class.__name__} instances: {e}", exc_info=True)
            raise

    @staticmethod
    def query(
        db: Session,
        model_class: Type[DeclarativeMeta],
        page: int = 1,
        per_page: int = 10,
        **filters: Any,
    ) -> Tuple[List[DeclarativeMeta], int]:
        """
        Query instances of the given model class with optional filters and pagination.

        Args:
            db (Session): The database session.
            model_class (Type[DeclarativeMeta]): The SQLAlchemy model class.
            page (int): The page number (1-indexed).
            per_page (int): The number of items per page.
            **filters: Keyword arguments for filtering the query.

        Returns:
            Tuple[List[DeclarativeMeta], int]: A tuple containing the list of instances and the total count.
        """
        # Refactor this. Maybe add a method for all the comparisons.
        try:
            query = db.query(model_class)
            filter_conditions = []
            for attr, value in filters.items():
                if isinstance(value, (list, tuple)):
                    if len(value) == 2 and value[0] in ['>', '<', '>=', '<=', '==', '!=']:
                        op, val = value
                        column = getattr(model_class, attr)
                        if op == '>':
                            filter_conditions.append(column > val)
                        elif op == '<':
                            filter_conditions.append(column < val)
                        elif op == '>=':
                            filter_conditions.append(column >= val)
                        elif op == '<=':
                            filter_conditions.append(column <= val)
                        elif op == '==':
                            filter_conditions.append(column == val)
                        elif op == '!=':
                            filter_conditions.append(column != val)
                    else:
                        filter_conditions.append(getattr(model_class, attr).in_(value))
                else:
                    filter_conditions.append(getattr(model_class, attr) == value)

            if filter_conditions:
                query = query.filter(and_(*filter_conditions))

            total = query.count()
            instances = query.offset((page - 1) * per_page).limit(per_page).all()
            logger.info(
                f"Queried {model_class.__name__} with filters: {filters}. Page {page}, {len(instances)} items. Total: {total}")
            return instances, total
        except SQLAlchemyError as e:
            logger.error(f"Database error querying {model_class.__name__} with filters {filters}: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error querying {model_class.__name__} with filters {filters}: {e}", exc_info=True)
            raise
