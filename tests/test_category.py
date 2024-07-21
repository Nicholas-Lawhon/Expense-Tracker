import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from expense_tracker.db.models import Base, Category
from expense_tracker.db.operations import BaseOperations

# Setup test database
@pytest.fixture(scope="module")
def engine():
    return create_engine("sqlite:///:memory:")

@pytest.fixture(scope="module")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def dbsession(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()

def test_create_category(dbsession):
    # Create a new category
    new_category = BaseOperations.create(
        dbsession,
        Category,
        name="Groceries",
        description="Food and household items"
    )

    # Check if the category was created
    assert new_category.id is not None
    assert new_category.name == "Groceries"
    assert new_category.description == "Food and household items"

def test_read_category(dbsession):
    # Create a category
    category = BaseOperations.create(
        dbsession,
        Category,
        name="Entertainment",
        description="Movies, games, etc."
    )

    # Read the category
    read_category = BaseOperations.read(dbsession, Category, category.id)

    # Check if the read category matches the created one
    assert read_category is not None
    assert read_category.name == "Entertainment"
    assert read_category.description == "Movies, games, etc."

def test_update_category(dbsession):
    # Create a category
    category = BaseOperations.create(
        dbsession,
        Category,
        name="Utilities",
        description="Electricity, water, gas"
    )

    # Update the category
    updated_category = BaseOperations.update(
        dbsession,
        Category,
        category.id,
        description="Electricity, water, gas, internet"
    )

    # Check if the category was updated
    assert updated_category is not None
    assert updated_category.name == "Utilities"
    assert updated_category.description == "Electricity, water, gas, internet"

def test_delete_category(dbsession):
    # Create a category
    category = BaseOperations.create(
        dbsession,
        Category,
        name="To Be Deleted",
        description="This category will be deleted"
    )

    # Delete the category
    deleted = BaseOperations.delete(dbsession, Category, category.id)

    # Check if the category was deleted
    assert deleted is True
    assert BaseOperations.read(dbsession, Category, category.id) is None

def test_get_all_categories(dbsession):
    # Create multiple categories
    for i in range(5):
        BaseOperations.create(
            dbsession,
            Category,
            name=f"Category {i}",
            description=f"Description for category {i}"
        )

    # Get all categories
    categories, total = BaseOperations.get_all(dbsession, Category, page=1, per_page=10)

    # Check if all categories were retrieved
    assert len(categories) == 5
    assert total == 5

def test_query_categories(dbsession):
    # Create categories with different names
    for name in ["Food", "Transport", "Housing", "Entertainment", "Misc"]:
        BaseOperations.create(
            dbsession,
            Category,
            name=name,
            description=f"Expenses related to {name.lower()}"
        )

    # Query categories with names starting with 'F' or 'T'
    ft_categories, total = BaseOperations.query(
        dbsession,
        Category,
        page=1,
        per_page=10,
        name=["Food", "Transport"]
    )

    # Check if only 'Food' and 'Transport' categories were retrieved
    assert len(ft_categories) == 2
    assert total == 2
    assert all(c.name in ["Food", "Transport"] for c in ft_categories)

    # Query categories with names not equal to 'Misc'
    non_misc_categories, total = BaseOperations.query(
        dbsession,
        Category,
        page=1,
        per_page=10,
        name=['!=', 'Misc']
    )

    # Check if all categories except 'Misc' were retrieved
    assert len(non_misc_categories) == 4
    assert total == 4
    assert all(c.name != "Misc" for c in non_misc_categories)