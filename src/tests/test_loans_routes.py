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

def test_create_loan(client, init_database):
    response = client.post('/loans', json={
        'book_id': 1,         # Replace with a valid book ID
        'customer_id': 1,     # Replace with a valid customer ID
        'loan_date': '2024-01-01'
    })
    assert response.status_code == 201
    assert response.json['message'] == "Loan created successfully"

def test_get_all_loans(client, init_database):
    response = client.get('/loans')
    assert response.status_code == 200
    assert isinstance(response.json, list)  # Check if the response is a list

def test_get_loan(client, init_database):
    response = client.get('/loans/1')  # Replace 1 with an existing loan ID
    assert response.status_code == 200
    assert 'id' in response.json
    assert response.json['id'] == 1

def test_get_nonexistent_loan(client, init_database):
    response = client.get('/loans/9999')  # Assuming 9999 does not exist
    assert response.status_code == 404
    assert response.json['error'] == "Loan not found"

def test_update_loan(client, init_database):
    response = client.put('/loans/1', json={
        'book_id': 1,         # Replace with a valid book ID
        'customer_id': 1,     # Replace with a valid customer ID
        'loan_date': '2024-01-02',
        'return_date': '2024-01-15'
    })
    assert response.status_code == 200
    assert response.json['message'] == "Loan updated successfully"

def test_delete_loan(client, init_database):
    response = client.delete('/loans/1')  # Replace 1 with an existing loan ID
    assert response.status_code == 200
    assert response.json['message'] == "Loan hidden successfully"

