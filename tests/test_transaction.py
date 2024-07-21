import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from expense_tracker.db.models import Base, Transaction, TransactionType
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

def test_create_transaction(dbsession):
    # Create a new transaction
    new_transaction = BaseOperations.create(
        dbsession,
        Transaction,
        name="Test Transaction",
        amount=100.00,
        type=TransactionType.EXPENSE,
        date=date.today()
    )

    # Check if the transaction was created
    assert new_transaction.id is not None
    assert new_transaction.name == "Test Transaction"
    assert new_transaction.amount == 100.00

def test_read_transaction(dbsession):
    # Create a transaction
    transaction = BaseOperations.create(
        dbsession,
        Transaction,
        name="Read Test",
        amount=50.00,
        type=TransactionType.INCOME,
        date=date.today()
    )

    # Read the transaction
    read_transaction = BaseOperations.read(dbsession, Transaction, transaction.id)

    # Check if the read transaction matches the created one
    assert read_transaction is not None
    assert read_transaction.name == "Read Test"
    assert read_transaction.amount == 50.00

def test_update_transaction(dbsession):
    # Create a transaction
    transaction = BaseOperations.create(
        dbsession,
        Transaction,
        name="Update Test",
        amount=75.00,
        type=TransactionType.EXPENSE,
        date=date.today()
    )

    # Update the transaction
    updated_transaction = BaseOperations.update(
        dbsession,
        Transaction,
        transaction.id,
        name="Updated Transaction",
        amount=100.00
    )

    # Check if the transaction was updated
    assert updated_transaction is not None
    assert updated_transaction.name == "Updated Transaction"
    assert updated_transaction.amount == 100.00
    assert updated_transaction.type == TransactionType.EXPENSE  # Unchanged field

def test_delete_transaction(dbsession):
    # Create a transaction
    transaction = BaseOperations.create(
        dbsession,
        Transaction,
        name="Delete Test",
        amount=25.00,
        type=TransactionType.INCOME,
        date=date.today()
    )

    # Delete the transaction
    deleted = BaseOperations.delete(dbsession, Transaction, transaction.id)

    # Check if the transaction was deleted
    assert deleted is True
    assert BaseOperations.read(dbsession, Transaction, transaction.id) is None

def test_get_all_transactions(dbsession):
    # Create multiple transactions
    for i in range(5):
        BaseOperations.create(
            dbsession,
            Transaction,
            name=f"Transaction {i}",
            amount=10.00 * i,
            type=TransactionType.EXPENSE,
            date=date.today() - timedelta(days=i)
        )

    # Get all transactions
    transactions, total = BaseOperations.get_all(dbsession, Transaction, page=1, per_page=10)

    # Check if all transactions were retrieved
    assert len(transactions) == 5
    assert total == 5

def test_query_transactions(dbsession):
    # Create transactions with different types and amounts
    for i in range(3):
        BaseOperations.create(
            dbsession,
            Transaction,
            name=f"Expense {i}",
            amount=10.00 * (i + 1),
            type=TransactionType.EXPENSE,
            date=date.today() - timedelta(days=i)
        )
    for i in range(2):
        BaseOperations.create(
            dbsession,
            Transaction,
            name=f"Income {i}",
            amount=100.00 * (i + 1),
            type=TransactionType.INCOME,
            date=date.today() - timedelta(days=i)
        )

    # Query only expense transactions
    expenses, total = BaseOperations.query(
        dbsession,
        Transaction,
        page=1,
        per_page=10,
        type=TransactionType.EXPENSE
    )

    # Check if only expense transactions were retrieved
    assert len(expenses) == 3
    assert total == 3
    assert all(t.type == TransactionType.EXPENSE for t in expenses)

    # Query transactions with amount greater than 50
    large_transactions, total = BaseOperations.query(
        dbsession,
        Transaction,
        page=1,
        per_page=10,
        amount=['>', 50]
    )

    # Check if only transactions with amount > 50 were retrieved
    assert len(large_transactions) == 2
    assert total == 2
    assert all(t.amount > 50 for t in large_transactions)

    # Query transactions with amount less than or equal to 30
    small_transactions, total = BaseOperations.query(
        dbsession,
        Transaction,
        page=1,
        per_page=10,
        amount=['<=', 30]
    )

    # Check if only transactions with amount <= 30 were retrieved
    assert len(small_transactions) == 3
    assert total == 3
    assert all(t.amount <= 30 for t in small_transactions)

    # Query transactions with multiple conditions
    specific_transactions, total = BaseOperations.query(
        dbsession,
        Transaction,
        page=1,
        per_page=10,
        type=TransactionType.EXPENSE,
        amount=['<', 25]
    )

    # Check if only expense transactions with amount < 25 were retrieved
    assert len(specific_transactions) == 2
    assert total == 2
    assert all(t.type == TransactionType.EXPENSE and t.amount < 25 for t in specific_transactions)
