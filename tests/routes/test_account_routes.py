import pytest
from expense_tracker.app import app
from expense_tracker.models import Account
from expense_tracker.db.operations import BaseOperations


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_create_account(client):
    response = client.post('/accounts/', json={
        'name': 'Test Account',
        'balance': 1000.00
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'Test Account'
    assert data['balance'] == 1000.00


def test_get_all_accounts(client):
    response = client.get('/accounts/')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_get_account(client):
    # First, create an account
    create_response = client.post('/accounts/', json={
        'name': 'Test Account',
        'balance': 1000.00
    })
    account_id = create_response.get_json()['id']

    # Then, get the account
    response = client.get(f'/accounts/{account_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Test Account'
    assert data['balance'] == 1000.00
