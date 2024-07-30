import pytest
from expense_tracker.app import app
from expense_tracker.models import Category
from expense_tracker.db.operations import BaseOperations


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_create_category(client):
    response = client.post('/categories/', json={
        'name': 'Test Category',
        'description': 'This is a test category'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'Test Category'
    assert data['description'] == 'This is a test category'


def test_get_all_categories(client):
    response = client.get('/categories/')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_get_category(client):
    # First, create a category
    create_response = client.post('/categories/', json={
        'name': 'Test Category',
        'description': 'This is a test category'
    })
    category_id = create_response.get_json()['id']

    # Then, get the category
    response = client.get(f'/categories/{category_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Test Category'
    assert data['description'] == 'This is a test category'

# Add more tests for update and delete operations
