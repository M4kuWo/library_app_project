import pytest
from library_app_project.app import create_app  
from library_app_project.database import get_db  

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client

@pytest.fixture
def init_database():
    # Setup code to initialize the database, e.g., create tables and insert test data
    pass  # Implement as needed

def test_create_customer(client, init_database):
    response = client.post('/customers', json={
        'name': 'John Doe',
        'city': 'New York',
        'age': 30
    })
    assert response.status_code == 201
    assert response.json['message'] == "Customer created successfully"

def test_get_all_customers(client, init_database):
    response = client.get('/customers')
    assert response.status_code == 200
    assert isinstance(response.json, list)  # Check if the response is a list

def test_get_customer(client, init_database):
    response = client.get('/customers/1')  # Replace 1 with an existing customer ID
    assert response.status_code == 200
    assert 'id' in response.json
    assert response.json['id'] == 1

def test_get_nonexistent_customer(client, init_database):
    response = client.get('/customers/9999')  # Assuming 9999 does not exist
    assert response.status_code == 404
    assert response.json['error'] == "Customer not found"

def test_update_customer(client, init_database):
    response = client.put('/customers/1', json={
        'name': 'Jane Doe',
        'city': 'Los Angeles',
        'age': 28
    })
    assert response.status_code == 200
    assert response.json['message'] == "Customer updated successfully"

def test_delete_customer(client, init_database):
    response = client.delete('/customers/1')  # Replace 1 with an existing customer ID
    assert response.status_code == 200
    assert response.json['message'] == "Customer hidden successfully"

