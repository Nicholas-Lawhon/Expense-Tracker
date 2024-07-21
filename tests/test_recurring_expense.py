import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from expense_tracker.db.models import Base, RecurringExpense, Category, Account, IntervalType
from expense_tracker.db.operations import BaseOperations
from datetime import date, timedelta

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

@pytest.fixture
def category(dbsession):
    return BaseOperations.create(
        dbsession,
        Category,
        name="Subscriptions",
        description="Regular subscription services"
    )

@pytest.fixture
def account(dbsession):
    return BaseOperations.create(
        dbsession,
        Account,
        name="Credit Card",
        balance=0.00
    )

def test_create_recurring_expense(dbsession, category, account):
    # Create a new recurring expense
    new_recurring_expense = BaseOperations.create(
        dbsession,
        RecurringExpense,
        name="Netflix",
        amount=15.99,
        interval=IntervalType.MONTHLY,
        billing_date=date.today(),
        category_id=category.id,
        account_id=account.id
    )

    # Check if the recurring expense was created
    assert new_recurring_expense.id is not None
    assert new_recurring_expense.name == "Netflix"
    assert new_recurring_expense.amount == 15.99
    assert new_recurring_expense.interval == IntervalType.MONTHLY

def test_read_recurring_expense(dbsession, category, account):
    # Create a recurring expense
    recurring_expense = BaseOperations.create(
        dbsession,
        RecurringExpense,
        name="Gym Membership",
        amount=50.00,
        interval=IntervalType.MONTHLY,
        billing_date=date.today(),
        category_id=category.id,
        account_id=account.id
    )

    # Read the recurring expense
    read_recurring_expense = BaseOperations.read(dbsession, RecurringExpense, recurring_expense.id)

    # Check if the read recurring expense matches the created one
    assert read_recurring_expense is not None
    assert read_recurring_expense.name == "Gym Membership"
    assert read_recurring_expense.amount == 50.00

def test_update_recurring_expense(dbsession, category, account):
    # Create a recurring expense
    recurring_expense = BaseOperations.create(
        dbsession,
        RecurringExpense,
        name="Spotify",
        amount=9.99,
        interval=IntervalType.MONTHLY,
        billing_date=date.today(),
        category_id=category.id,
        account_id=account.id
    )

    # Update the recurring expense
    updated_recurring_expense = BaseOperations.update(
        dbsession,
        RecurringExpense,
        recurring_expense.id,
        amount=12.99,
        interval=IntervalType.ANNUALLY
    )

    # Check if the recurring expense was updated
    assert updated_recurring_expense is not None
    assert updated_recurring_expense.name == "Spotify"
    assert updated_recurring_expense.amount == 12.99
    assert updated_recurring_expense.interval == IntervalType.ANNUALLY

def test_delete_recurring_expense(dbsession, category, account):
    # Create a recurring expense
    recurring_expense = BaseOperations.create(
        dbsession,
        RecurringExpense,
        name="To Be Deleted",
        amount=5.00,
        interval=IntervalType.MONTHLY,
        billing_date=date.today(),
        category_id=category.id,
        account_id=account.id
    )

    # Delete the recurring expense
    deleted = BaseOperations.delete(dbsession, RecurringExpense, recurring_expense.id)

    # Check if the recurring expense was deleted
    assert deleted is True
    assert BaseOperations.read(dbsession, RecurringExpense, recurring_expense.id) is None

def test_get_all_recurring_expenses(dbsession, category, account):
    # Create multiple recurring expenses
    for i in range(5):
        BaseOperations.create(
            dbsession,
            RecurringExpense,
            name=f"Recurring Expense {i}",
            amount=10.00 * (i + 1),
            interval=IntervalType.MONTHLY,
            billing_date=date.today() + timedelta(days=i),
            category_id=category.id,
            account_id=account.id
        )

    # Get all recurring expenses
    recurring_expenses, total = BaseOperations.get_all(dbsession, RecurringExpense, page=1, per_page=10)

    # Check if all recurring expenses were retrieved
    assert len(recurring_expenses) == 5
    assert total == 5

def test_query_recurring_expenses(dbsession, category, account):
    # Create recurring expenses with different amounts and intervals
    for i in range(3):
        BaseOperations.create(
            dbsession,
            RecurringExpense,
            name=f"Monthly Expense {i}",
            amount=20.00 * (i + 1),  # This will create expenses with amounts 20, 40, 60
            interval=IntervalType.MONTHLY,
            billing_date=date.today(),
            category_id=category.id,
            account_id=account.id
        )
    for i in range(2):
        BaseOperations.create(
            dbsession,
            RecurringExpense,
            name=f"Annual Expense {i}",
            amount=200.00 * (i + 1),  # This will create expenses with amounts 200, 400
            interval=IntervalType.ANNUALLY,
            billing_date=date.today(),
            category_id=category.id,
            account_id=account.id
        )

    # Query only monthly recurring expenses
    monthly_expenses, total = BaseOperations.query(
        dbsession,
        RecurringExpense,
        page=1,
        per_page=10,
        interval=IntervalType.MONTHLY
    )

    # Check if only monthly recurring expenses were retrieved
    assert len(monthly_expenses) == 3
    assert total == 3
    assert all(re.interval == IntervalType.MONTHLY for re in monthly_expenses)

    # Query recurring expenses with amount greater than 50
    large_expenses, total = BaseOperations.query(
        dbsession,
        RecurringExpense,
        page=1,
        per_page=10,
        amount=['>', 50]
    )

    # Check if only recurring expenses with amount > 50 were retrieved
    assert len(large_expenses) == 3  # The 60, 200, and 400 expenses should be > 50
    assert total == 3
    assert all(re.amount > 50 for re in large_expenses)