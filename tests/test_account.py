import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from expense_tracker.db.models import Base, Account
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


def test_create_account(dbsession):
    new_account = BaseOperations.create(
        dbsession,
        Account,
        name="Checking Account",
        balance=1000.00
    )
    assert new_account.id is not None
    assert new_account.name == "Checking Account"
    assert new_account.balance == 1000.00


def test_read_account(dbsession):
    account = BaseOperations.create(
        dbsession,
        Account,
        name="Savings Account",
        balance=500.00
    )
    read_account = BaseOperations.read(dbsession, Account, account.id)
    assert read_account is not None
    assert read_account.name == "Savings Account"
    assert read_account.balance == 500.00


def test_update_account(dbsession):
    account = BaseOperations.create(
        dbsession,
        Account,
        name="Credit Card",
        balance=0.00
    )
    updated_account = BaseOperations.update(
        dbsession,
        Account,
        account.id,
        balance=-100.00
    )
    assert updated_account.balance == -100.00


def test_delete_account(dbsession):
    account = BaseOperations.create(
        dbsession,
        Account,
        name="To Be Deleted",
        balance=1.00
    )
    deleted = BaseOperations.delete(dbsession, Account, account.id)
    assert deleted is True
    assert BaseOperations.read(dbsession, Account, account.id) is None


def test_get_all_accounts(dbsession):
    for i in range(5):
        BaseOperations.create(
            dbsession,
            Account,
            name=f"Account {i}",
            balance=100.00 * i
        )
    accounts, total = BaseOperations.get_all(dbsession, Account, page=1, per_page=10)
    assert len(accounts) == 5
    assert total == 5


def test_query_accounts(dbsession):
    for i in range(3):
        BaseOperations.create(
            dbsession,
            Account,
            name=f"Low Balance {i}",
            balance=50.00 * i
        )
    for i in range(2):
        BaseOperations.create(
            dbsession,
            Account,
            name=f"High Balance {i}",
            balance=1000.00 * (i + 1)
        )

    low_balance_accounts, total = BaseOperations.query(
        dbsession,
        Account,
        page=1,
        per_page=10,
        balance=['<', 100]
    )
    assert len(low_balance_accounts) == 2
    assert total == 2
    assert all(a.balance < 100 for a in low_balance_accounts)

    high_balance_accounts, total = BaseOperations.query(
        dbsession,
        Account,
        page=1,
        per_page=10,
        balance=['>=', 1000]
    )
    assert len(high_balance_accounts) == 2
    assert total == 2
    assert all(a.balance >= 1000 for a in high_balance_accounts)