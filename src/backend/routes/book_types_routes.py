from flask import Blueprint, jsonify
from sqlalchemy.orm import Session
# from ..models import BookType
from ...database import get_db, BookType

# Create a Blueprint for book types
book_types_routes_bp = Blueprint('book_types', __name__)

@book_types_routes_bp.route('/', methods=['GET'])
def get_all_book_types():
    db: Session = next(get_db())
    book_types = db.query(BookType).filter_by(hidden=False).all()
    
    return jsonify([{
        "id": bt.id,  # Use the loop variable `bt`
        "type": bt.type,
        "max_loan_duration": bt.max_loan_duration,
        "hidden": bt.hidden
    } for bt in book_types]), 200


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
