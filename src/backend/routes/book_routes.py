from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from ..models import Book
from ...database import get_db, BookType 

book_routes_bp = Blueprint('book_routes', __name__)

@book_routes_bp.route('/', methods=['POST'])
def create_book():
    data = request.json
    try:
        # Validate that the book type exists in the BookType model
        book_type_value = data['type']  # Expecting 'type' in the request body
        
        db: Session = next(get_db())
        
        # Query the BookType to check if the provided type exists as an ID
        book_type = db.query(BookType).filter(BookType.id == book_type_value).first()
        
        if not book_type:
            return jsonify({"error": "Invalid book type ID"}), 400

        # Create a new book with the validated book type
        new_book = Book(
            title=data['title'],
            author=data['author'],
            year_published=data['year_published'],
            book_type_id=book_type_value,  # Use the valid book type ID
            hidden=False
        )
        
        db.add(new_book)
        db.commit()
        db.refresh(new_book)
        
        return jsonify({"message": "Book created successfully", "book": {
            "id": new_book.id,
            "title": new_book.title,
            "author": new_book.author,
            "year_published": new_book.year_published,
            "type": new_book.book_type_id,  # Send the type as 'type'
            "hidden": new_book.hidden
        }}), 201

    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@book_routes_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    db: Session = next(get_db())
    book = db.query(Book).options(joinedload(Book.book_type)).filter(Book.id == book_id).first()
    
    if book:
        return jsonify({
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "year_published": book.year_published,
            "type": book.book_type.type if book.book_type else None,  # Access the joined book_type
            "hidden": book.hidden
        }), 200
    return jsonify({"error": "Book not found"}), 404

@book_routes_bp.route('/', methods=['GET'])
def get_all_books():
    db: Session = next(get_db())
    books = db.query(Book).options(joinedload(Book.book_type)).filter(Book.hidden == False).all()  # Use joinedload

    books_list = [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "year_published": book.year_published,
            "type": book.book_type.type if book.book_type else None,  # Access the joined book_type
            "hidden": book.hidden
        } for book in books
    ]
    
    return jsonify(books_list), 200

@book_routes_bp.route('/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json
    try:
        db: Session = next(get_db())
        
        # Find the book to update
        updated_book = db.query(Book).filter(Book.id == book_id).first()
        if not updated_book:
            return jsonify({"error": "Book not found"}), 404

        # Validate if the 'type' field exists in the request data
        if 'type' in data:
            book_type_value = data['type']  # Expecting 'type' in the request body
            
            # Query the BookType to check if the provided type exists as an ID
            book_type = db.query(BookType).filter(BookType.id == book_type_value).first()

            if not book_type:
                return jsonify({"error": "Invalid book type ID"}), 400
            
            # Update book type only if it's provided
            updated_book.book_type_id = book_type_value

        # Update fields only if they are provided in the request body
        if 'title' in data:
            updated_book.title = data['title']
        if 'author' in data:
            updated_book.author = data['author']
        if 'year_published' in data:
            updated_book.year_published = data['year_published']
        if 'hidden' in data:
            updated_book.hidden = data.get('hidden', False)

        # Commit changes to the database
        db.commit()
        
        return jsonify({"message": "Book updated successfully"}), 200

    # Handle missing fields specifically
    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    
    # Handle other exceptions (e.g., database errors, etc.)
    except Exception as e:
        return jsonify({"error": str(e)}), 400



@book_routes_bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:
        db: Session = next(get_db())
        book = db.query(Book).filter(Book.id == book_id).one_or_none()  # Change to one_or_none for clarity
        if not book:
            return jsonify({"error": "Book not found"}), 404

        book.hidden = True  # Set hidden to True instead of deleting
        db.commit()
        
        return jsonify({"message": "Book hidden successfully"}), 204  # Return 204 No Content

    except Exception as e:
        db.rollback()  # Ensure the session is rolled back if there's an error
        return jsonify({"error": str(e)}), 400

