from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
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
    book = db.query(Book).filter(Book.id == book_id).first()
    booktype = db.query(BookType).filter(BookType.id == book_id).first()
    if book:
        return jsonify({
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "year_published": book.year_published,
            "type": booktype.type,  # Display the enum name (e.g., "FICTION" or "NONFICTION")
            "hidden": book.hidden
        }), 200
    return jsonify({"error": "Book not found"}), 404

@book_routes_bp.route('/', methods=['GET'])
def get_all_books():
    db: Session = next(get_db())
    books = db.query(Book).filter(Book.hidden == False).all()
    books_list = [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "year_published": book.year_published,
            "type": book.type.name,  # Enum name
            "hidden": book.hidden
        } for book in books
    ]
    return jsonify(books_list), 200

@book_routes_bp.route('/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json
    try:
        db: Session = next(get_db())
        updated_book = db.query(Book).filter(Book.id == book_id).first()
        if not updated_book:
            return jsonify({"error": "Book not found"}), 404

        updated_book.title = data['title']
        updated_book.author = data['author']
        updated_book.year_published = data['year_published']
        updated_book.type = BookTypeEnum(data['type'])  # Assuming type is passed correctly
        updated_book.hidden = data.get('hidden', False)

        db.commit()
        return jsonify({"message": "Book updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@book_routes_bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:
        db: Session = next(get_db())
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            return jsonify({"error": "Book not found"}), 404

        book.hidden = True 
        db.commit()
        return jsonify({"message": "Book hidden successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
