import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from expense_tracker.db.models import Base, Budget, Category
from expense_tracker.db.operations import BaseOperations
from datetime import date, timedelta

# ADD COMMENTS TO THIS MODULE

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


@pytest.fixture
def category(dbsession):
    return BaseOperations.create(
        dbsession,
        Category,
        name="Test Category",
        description="For testing budgets"
    )


def test_create_budget(dbsession, category):
    new_budget = BaseOperations.create(
        dbsession,
        Budget,
        category_id=category.id,
        amount=300.00,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30)
    )
    assert new_budget.id is not None
    assert new_budget.amount == 300.00
    assert new_budget.category_id == category.id


def test_read_budget(dbsession, category):
    budget = BaseOperations.create(
        dbsession,
        Budget,
        category_id=category.id,
        amount=200.00,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30)
    )
    read_budget = BaseOperations.read(dbsession, Budget, budget.id)
    assert read_budget is not None
    assert read_budget.amount == 200.00
    assert read_budget.category_id == category.id


def test_update_budget(dbsession, category):
    budget = BaseOperations.create(
        dbsession,
        Budget,
        category_id=category.id,
        amount=100.00,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30)
    )
    updated_budget = BaseOperations.update(
        dbsession,
        Budget,
        budget.id,
        amount=150.00
    )
    assert updated_budget.amount == 150.00


def test_delete_budget(dbsession, category):
    budget = BaseOperations.create(
        dbsession,
        Budget,
        category_id=category.id,
        amount=50.00,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30)
    )
    deleted = BaseOperations.delete(dbsession, Budget, budget.id)
    assert deleted is True
    assert BaseOperations.read(dbsession, Budget, budget.id) is None


def test_get_all_budgets(dbsession, category):
    for i in range(5):
        BaseOperations.create(
            dbsession,
            Budget,
            category_id=category.id,
            amount=100.00 * (i + 1),
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30 * (i + 1))
        )
    budgets, total = BaseOperations.get_all(dbsession, Budget, page=1, per_page=10)
    assert len(budgets) == 5
    assert total == 5


def test_query_budgets(dbsession, category):
    # Create budgets with different amounts
    for i in range(5):
        BaseOperations.create(
            dbsession,
            Budget,
            category_id=category.id,
            amount=50.00 * (i + 1),  # This will create budgets with amounts 50, 100, 150, 200, 250
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )

    low_budgets, total = BaseOperations.query(
        dbsession,
        Budget,
        page=1,
        per_page=10,
        amount=['<', 100]
    )
    assert len(low_budgets) == 1  # Only the 50 budget should be less than 100
    assert total == 1
    assert all(b.amount < 100 for b in low_budgets)

    high_budgets, total = BaseOperations.query(
        dbsession,
        Budget,
        page=1,
        per_page=10,
        amount=['>=', 200]
    )
    assert len(high_budgets) == 2  # The 200 and 250 budgets should be >= 200
    assert total == 2
    assert all(b.amount >= 200 for b in high_budgets)