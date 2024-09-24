import pytest
from flask import Flask
from models import Book, BookTypeEnum
from library_app_project.app import create_app
from database import get_db

@pytest.fixture
def app():
    app = create_app()
    with app.app_context():
        # Create the database schema (e.g., create all tables)
        db = next(get_db())
        db.create_all()
        yield app
        db.drop_all()  # Clean up after tests

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_db():
    db = next(get_db())
    # Insert test data if necessary
    yield db
    # Clean up the database after tests

def test_create_book(client, init_db):
    response = client.post('/books', json={
        'name': 'Test Book',
        'author': 'Test Author',
        'year_published': 2024,
        'type': BookTypeEnum.FICTION.value  # Use the enum value as expected
    })
    assert response.status_code == 201
    assert b'Book created successfully' in response.data

def test_get_book(client, init_db):
    # First, create a book
    client.post('/books', json={
        'name': 'Test Book',
        'author': 'Test Author',
        'year_published': 2024,
        'type': BookTypeEnum.FICTION.value
    })

    response = client.get('/books/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Test Book'
    assert data['author'] == 'Test Author'
    assert data['year_published'] == 2024
    assert data['type'] == 'FICTION'  # Check for the enum name

def test_get_all_books(client, init_db):
    client.post('/books', json={
        'name': 'Test Book 1',
        'author': 'Test Author 1',
        'year_published': 2024,
        'type': BookTypeEnum.FICTION.value
    })
    client.post('/books', json={
        'name': 'Test Book 2',
        'author': 'Test Author 2',
        'year_published': 2023,
        'type': BookTypeEnum.NONFICTION.value
    })

    response = client.get('/books')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2  # Ensure two books are returned

def test_update_book(client, init_db):
    # First, create a book
    client.post('/books', json={
        'name': 'Test Book',
        'author': 'Test Author',
        'year_published': 2024,
        'type': BookTypeEnum.FICTION.value
    })

    response = client.put('/books/1', json={
        'name': 'Updated Book',
        'author': 'Updated Author',
        'year_published': 2025,
        'type': BookTypeEnum.NONFICTION.value,
        'hidden': False
    })
    assert response.status_code == 200
    assert b'Book updated successfully' in response.data

    # Verify the update
    response = client.get('/books/1')
    data = response.get_json()
    assert data['name'] == 'Updated Book'
    assert data['author'] == 'Updated Author'
    assert data['year_published'] == 2025
    assert data['type'] == 'NONFICTION'  # Check for the updated enum name

def test_delete_book(client, init_db):
    # First, create a book
    client.post('/books', json={
        'name': 'Test Book',
        'author': 'Test Author',
        'year_published': 2024,
        'type': BookTypeEnum.FICTION.value
    })

    response = client.delete('/books/1')
    assert response.status_code == 200
    assert b'Book hidden successfully' in response.data

    # Try to get the deleted book
    response = client.get('/books/1')
    assert response.status_code == 404
    assert b'Book not found' in response.data
