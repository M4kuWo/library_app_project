from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session
from sqlalchemy import or_  # Importing `or_` for filtering queries
from ...database import get_db, BookType

# Create a Blueprint for book types
book_types_routes_bp = Blueprint('book_types', __name__)

@book_types_routes_bp.route('/', methods=['GET'])
def get_all_book_types():
    db: Session = next(get_db())

    # Get the search parameter for type or ID
    search_value = request.args.get('search', '')

    # Start the query, filtering out hidden book types
    query = db.query(BookType).filter_by(hidden=False)

    # Add search functionality for type or ID (case insensitive)
    if search_value:
        search_pattern = f"%{search_value}%"
        query = query.filter(
            or_(
                BookType.type.ilike(search_pattern),      # Search by type
                BookType.id.ilike(search_pattern)         # Search by ID
            )
        )

    # Fetch book types based on the query
    book_types = query.all()

    # Build the response
    book_types_list = [{
        "id": bt.id,
        "type": bt.type,
        "max_loan_duration": bt.max_loan_duration,
        "hidden": bt.hidden
    } for bt in book_types]
    
    return jsonify(book_types_list), 200


@book_types_routes_bp.route('/<int:book_type_id>', methods=['GET'])
def get_book_type(book_type_id):
    db: Session = next(get_db())
    book_type = db.query(BookType).filter_by(id=book_type_id, hidden=False).first()
    if book_type:
        return jsonify({
            "id": book_type.id,
            "type": book_type.type, 
            "max_loan_duration": book_type.max_loan_duration,
            "hidden": book_type.hidden
        }), 200
    return jsonify({"message": "Book type not found"}), 404
