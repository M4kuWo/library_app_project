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
    # This can involve creating a test database or using a mock database
    pass  # Implement as needed

def test_get_all_book_types(client, init_database):
    response = client.get('/book_types')
    assert response.status_code == 200
    assert isinstance(response.json, list)  # Check if the response is a list

def test_get_book_type(client, init_database):
    response = client.get('/book_types/1')  # Replace 1 with an existing book type ID
    assert response.status_code == 200
    assert 'id' in response.json
    assert response.json['id'] == 1

def test_get_nonexistent_book_type(client, init_database):
    response = client.get('/book_types/9999')  # Assuming 9999 does not exist
    assert response.status_code == 404
    assert response.json['message'] == "Book type not found"