import pytest
from expense_tracker.app import app
from expense_tracker.models import Budget, Category
from expense_tracker.db.operations import BaseOperations
from datetime import date


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def category(client):
    response = client.post('/categories/', json={'name': 'Test Category'})
    return response.get_json()


def test_create_budget(client, category):
    response = client.post('/budgets/', json={
        'name': 'Test Budget',
        'amount': 1000.00,
        'category_id': category['id'],
        'start_date': str(date.today()),
        'end_date': str(date.today().replace(month=date.today().month + 1))
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'Test Budget'
    assert data['amount'] == 1000.00
    assert data['category_id'] == category['id']


def test_get_all_budgets(client):
    response = client.get('/budgets/')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_get_budget(client, category):
    # First, create a budget
    create_response = client.post('/budgets/', json={
        'name': 'Test Budget',
        'amount': 1000.00,
        'category_id': category['id'],
        'start_date': str(date.today()),
        'end_date': str(date.today().replace(month=date.today().month + 1))
    })
    budget_id = create_response.get_json()['id']

    # Then, get the budget
    response = client.get(f'/budgets/{budget_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Test Budget'
    assert data['amount'] == 1000.00
    assert data['category_id'] == category['id']

# Add more tests for update and delete operations
