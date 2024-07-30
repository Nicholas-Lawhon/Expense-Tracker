import pytest
from expense_tracker.app import app
from expense_tracker.models import Transaction, Account, Category
from expense_tracker.db.operations import BaseOperations
from datetime import date


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def account(client):
    response = client.post('/accounts/', json={'name': 'Test Account', 'balance': 1000.00})
    return response.get_json()


@pytest.fixture
def category(client):
    response = client.post('/categories/', json={'name': 'Test Category'})
    return response.get_json()


def test_create_transaction(client, account, category):
    response = client.post('/transactions/', json={
        'name': 'Test Transaction',
        'amount': 100.00,
        'account_id': account['id'],
        'category_id': category['id'],
        'date': str(date.today()),
        'type': 'EXPENSE',
        'interval': 'ONCE'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'Test Transaction'
    assert data['amount'] == 100.00
    assert data['account_id'] == account['id']
    assert data['category_id'] == category['id']
    assert data['type'] == 'EXPENSE'
    assert data['interval'] == 'ONCE'


def test_get_all_transactions(client):
    response = client.get('/transactions/')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_get_transaction(client, account, category):
    # First, create a transaction
    create_response = client.post('/transactions/', json={
        'name': 'Test Transaction',
        'amount': 100.00,
        'account_id': account['id'],
        'category_id': category['id'],
        'date': str(date.today()),
        'type': 'EXPENSE',
        'interval': 'ONCE'
    })
    transaction_id = create_response.get_json()['id']

    # Then, get the transaction
    response = client.get(f'/transactions/{transaction_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Test Transaction'
    assert data['amount'] == 100.00
    assert data['account_id'] == account['id']
    assert data['category_id'] == category['id']
    assert data['type'] == 'EXPENSE'
    assert data['interval'] == 'ONCE'

# Add more tests for update and delete operations
