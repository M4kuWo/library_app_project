from flask import Blueprint, jsonify
from sqlalchemy.orm import Session
from ...database import get_db, Category

categories_routes_bp = Blueprint('categories_routes', __name__)

@categories_routes_bp.route('/', methods=['GET'])
def get_all_categories():
    db: Session = next(get_db())

    # Fetch all categories from the database
    categories = db.query(Category).all()

    # Build the response
    categories_list = [{"id": category.id, "name": category.name} for category in categories]
    
    return jsonify(categories_list), 200


@categories_routes_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    db: Session = next(get_db())
    
    # Query the category with the given ID
    category = db.query(Category).filter(Category.id == category_id).first()

    if category:
        return jsonify({
            "id": category.id,
            "name": category.name
        }), 200
    
    return jsonify({"error": "Category not found"}), 404
