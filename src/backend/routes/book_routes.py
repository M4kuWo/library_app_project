from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Book, User
from ...database import get_db, BookType, Category
from http import HTTPStatus

book_routes_bp = Blueprint('book_routes', __name__)

def check_profile_level(required_level):
    # Get the current user's identity from the JWT token
    current_user_email = get_jwt_identity().get('email')
    
    db: Session = next(get_db())
    current_user = db.query(User).filter(User.email == current_user_email).first()

    if not current_user:
        return False  # User not found

    # Check if the current user's profile level is equal to or lower than the required level
    return current_user.profile <= required_level

def get_book_type_id(number_of_pages: int, db: Session) -> int:
    if number_of_pages >= 300:
        return 1  # LONG type
    elif 150 <= number_of_pages < 300:
        return 2  # MEDIUM type
    else:
        return 3  # SHORT type

@book_routes_bp.route('/', methods=['POST'])
@jwt_required()
def create_book():
    if not check_profile_level(2):  # Only allow admin (profile <= 2) to create books
        return jsonify({"error": "Unauthorized access"}), HTTPStatus.FORBIDDEN

    data = request.json
    try:
        # Validate that the book type and category exist
        category_value = data['category']
        number_of_pages = data['number_of_pages']

        db: Session = next(get_db())

        # Check if the category exists
        category = db.query(Category).filter(Category.id == category_value).first()
        if not category:
            return jsonify({"error": "Invalid category ID"}), HTTPStatus.BAD_REQUEST

        # Determine book type ID based on number of pages
        book_type_id = get_book_type_id(number_of_pages, db)

        # Create a new book with validated category and determined book type
        new_book = Book(
            title=data['title'],
            author=data['author'],
            category=category_value,
            cover_image=data.get('cover_image'),
            year_published=data['year_published'],
            book_type_id=book_type_id,
            number_of_pages=number_of_pages,  # Include this field
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
            "type": db.query(BookType).filter(BookType.id == book_type_id).first().type,  # Get type value
            "category": category.category,
            "cover_image": new_book.cover_image,
            "number_of_pages": new_book.number_of_pages,  # Add number_of_pages to response
            "hidden": int(new_book.hidden)  # Convert to 1 or 0
        }}), HTTPStatus.CREATED

    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST

@book_routes_bp.route('/bulk', methods=['POST'])
@jwt_required()
def bulk_create_books():
    if not check_profile_level(2):  # Only allow admin (profile <= 2) to create books
        return jsonify({"error": "Unauthorized access"}), HTTPStatus.FORBIDDEN

    data = request.json
    if not isinstance(data, list):
        return jsonify({"error": "Request body must be a list of books"}), HTTPStatus.BAD_REQUEST

    db: Session = next(get_db())
    created_books = []

    try:
        for book_data in data:
            category_value = book_data['category']
            number_of_pages = book_data['number_of_pages']  # Get the number of pages from the book data

            # Validate category
            category = db.query(Category).filter(Category.id == category_value).first()
            if not category:
                return jsonify({"error": f"Invalid category ID: {category_value}"}), HTTPStatus.BAD_REQUEST

            # Determine book type ID based on number of pages
            book_type_id = get_book_type_id(number_of_pages, db)

            # Create the new book object
            new_book = Book(
                title=book_data['title'],
                author=book_data['author'],
                category=category_value,
                cover_image=book_data.get('cover_image'),
                year_published=book_data['year_published'],
                book_type_id=book_type_id,  # Use the determined book type ID
                number_of_pages=number_of_pages,  # Include the number of pages
                hidden=book_data.get('hidden', False)  # Set hidden with default False
            )

            # Add book to the session
            db.add(new_book)
            db.flush()  # Flush the session to assign the new book's ID

            # Append the created book details to the response list
            created_books.append({
                "id": new_book.id,  # Now the ID will be available after flush
                "title": new_book.title,
                "author": new_book.author,
                "year_published": new_book.year_published,
                "type": db.query(BookType).filter(BookType.id == book_type_id).first().type,  # Get type value
                "category": category.category,
                "cover_image": new_book.cover_image,
                "number_of_pages": new_book.number_of_pages,  # Add number_of_pages to response
                "hidden": int(new_book.hidden)  # Convert hidden to 1 or 0
            })

        # Commit the transaction after all books are processed
        db.commit()

        return jsonify({"message": "Books created successfully", "books": created_books}), HTTPStatus.CREATED

    except KeyError as e:
        db.rollback()
        return jsonify({"error": f"Missing field in one of the book entries: {str(e)}"}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST

@book_routes_bp.route('/', methods=['GET'])
def get_all_books():
    db: Session = next(get_db())

    show_hidden = request.args.get('showHidden', default='0') == '1'
    hidden_only = request.args.get('hiddenOnly', default='0') == '1'
    search_term = request.args.get('search', default='')

    # Base query for books
    query = db.query(Book)

    # Apply filters based on parameters
    if hidden_only:
        # Show only books that are hidden
        query = query.filter(Book.hidden.is_(True))
    elif show_hidden:
        # Show both hidden and non-hidden books
        pass  # No additional filter needed
    
    # Show only non-hidden books by default
    else:
        query = query.filter(Book.hidden.is_(False))

    # Apply search filter if a search term is provided
    if search_term:
        query = query.filter(Book.title.ilike(f"%{search_term}%") | 
                             Book.author.ilike(f"%{search_term}%"))

    # Fetch the filtered books
    books = query.all()

    # Create the response data
    books_list = [{
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "year_published": book.year_published,
        "number_of_pages": book.number_of_pages,
        "type": book.book_type_id,
        "category": book.category,
        "cover_image": book.cover_image,
        "hidden": 1 if book.hidden else 0
    } for book in books]

    return jsonify({"books": books_list}), HTTPStatus.OK


@book_routes_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    db: Session = next(get_db())

    show_hidden = request.args.get('showHidden', default='0') == '1'

    # Filter the book by ID and hidden status based on show_hidden parameter
    query = db.query(Book).filter(Book.id == book_id)

    if not show_hidden:
        query = query.filter(Book.hidden.is_(False))

    book = query.one_or_none()

    if not book:
        return jsonify({"error": "Book not found"}), HTTPStatus.NOT_FOUND

    return jsonify({
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "year_published": book.year_published,
        "number_of_pages": book.number_of_pages, 
        "type": book.book_type_id,
        "category": book.category,
        "cover_image": book.cover_image,
        "hidden": 1 if book.hidden else 0
    }), HTTPStatus.OK

@book_routes_bp.route('/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    if not check_profile_level(2):  # Only allow admin (profile <= 2) to update books
        return jsonify({"error": "Unauthorized access"}), HTTPStatus.FORBIDDEN

    data = request.json
    try:
        db: Session = next(get_db())
        
        updated_book = db.query(Book).filter(Book.id == book_id).first()
        if not updated_book:
            return jsonify({"error": "Book not found"}), HTTPStatus.NOT_FOUND

        # Update category if provided
        if 'category' in data:
            category_value = data['category']
            category = db.query(Category).filter(Category.id == category_value).first()
            if not category:
                return jsonify({"error": "Invalid category ID"}), HTTPStatus.BAD_REQUEST
            updated_book.category = category_value

        # Update number of pages if provided and determine book type if it changes
        if 'number_of_pages' in data:
            number_of_pages = data['number_of_pages']
            updated_book.number_of_pages = number_of_pages
            # Only update the book type if the number of pages changes
            updated_book.book_type_id = get_book_type_id(number_of_pages, db)  # Update book type based on pages

        # Update other fields
        if 'title' in data:
            updated_book.title = data['title']
        if 'author' in data:
            updated_book.author = data['author']
        if 'year_published' in data:
            updated_book.year_published = data['year_published']
        if 'cover_image' in data:
            updated_book.cover_image = data['cover_image']
        if 'hidden' in data:
            updated_book.hidden = data.get('hidden', False)

        db.commit()

        # Fetch the updated book, book type, and category from the database
        updated_book = db.query(Book).filter(Book.id == book_id).first()
        book_type = db.query(BookType).filter(BookType.id == updated_book.book_type_id).first()
        category = db.query(Category).filter(Category.id == updated_book.category).first()

        # Prepare response data
        response_data = {
            "title": updated_book.title,
            "author": updated_book.author,
            "category": category.category if category else None,
            "cover_image": updated_book.cover_image,
            "year_published": updated_book.year_published,
            "book_type": book_type.type if book_type else None,
            "hidden": int(updated_book.hidden),  # Convert hidden to 1 or 0
            "number_of_pages": updated_book.number_of_pages  # Include number of pages in the response
        }

        return jsonify({"message": "Book updated successfully", "book": response_data}), HTTPStatus.OK

    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST

@book_routes_bp.route('/bulk', methods=['DELETE'])
@jwt_required()
def bulk_delete_books():
    if not check_profile_level(1):  # Only allow superadmin (profile == 1) to delete books
        return jsonify({"error": "Unauthorized access"}), HTTPStatus.FORBIDDEN

    data = request.json
    if not isinstance(data, list):
        return jsonify({"error": "Request body must be a list of book IDs"}), HTTPStatus.BAD_REQUEST

    db: Session = next(get_db())
    deleted_books = []

    for book_id in data:
        book = db.query(Book).filter(Book.id == book_id).one_or_none()
        if book:
            book.hidden = True
            deleted_books.append({"id": book_id, "title": book.title})
        else:
            return jsonify({"error": f"Book ID {book_id} not found"}), HTTPStatus.NOT_FOUND

    db.commit()
    
    return jsonify({"message": "Books hidden successfully", "deleted_books": deleted_books}), HTTPStatus.OK

@book_routes_bp.route('/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    if not check_profile_level(1):  # Only allow superadmin (profile == 1) to delete books
        return jsonify({"error": "Unauthorized access"}), HTTPStatus.FORBIDDEN

    db: Session = next(get_db())
    
    # Find the book by its ID
    book = db.query(Book).filter(Book.id == book_id).one_or_none()
    
    if not book:
        return jsonify({"error": f"Book ID {book_id} not found"}), HTTPStatus.NOT_FOUND

    # Mark the book as hidden (soft delete)
    book.hidden = True

    db.commit()

    return jsonify({"message": "Book hidden successfully", "book": {"id": book.id, "title": book.title}}), HTTPStatus.OK
