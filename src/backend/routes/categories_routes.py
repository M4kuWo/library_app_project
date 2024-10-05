from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session
from sqlalchemy import or_  # Importing `or_` for filtering queries
from ...database import get_db, Category

categories_routes_bp = Blueprint('categories_routes', __name__)

@categories_routes_bp.route('/', methods=['GET'])
def get_all_categories():
    db: Session = next(get_db())

    # Get the search parameter for category or ID
    search_value = request.args.get('search', '')

    # Start the query
    query = db.query(Category)

    # Add search functionality for category or ID (case insensitive)
    if search_value:
        search_pattern = f"%{search_value}%"
        query = query.filter(
            or_(
                Category.category.ilike(search_pattern),  # Search by category name
                Category.id.ilike(search_pattern)         # Search by ID
            )
        )

    # Fetch categories based on the query
    categories = query.all()

    # Build the response
    categories_list = [{"id": category.id, "category": category.category} for category in categories]
    
    return jsonify(categories_list), 200

@categories_routes_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    db: Session = next(get_db())
    
    # Query the category with the given ID
    category = db.query(Category).filter(Category.id == category_id).first()

    if category:
        return jsonify({
            "id": category.id,
            "category": category.category
        }), 200
    
    return jsonify({"error": "Category not found"}), 404
