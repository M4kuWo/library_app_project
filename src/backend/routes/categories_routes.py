from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from sqlalchemy import or_  # Importing `or_` for filtering queries
from ..models import User # For authentication
from ...database import get_db, Category

categories_routes_bp = Blueprint('categories_routes', __name__)

def check_profile_level(required_level):
    # Get the current user's identity from the JWT token
    current_user_email = get_jwt_identity().get('email')
    
    db: Session = next(get_db())
    current_user = db.query(User).filter(User.email == current_user_email).first()

    if not current_user:
        return False  # User not found

    # Check if the current user's profile level is equal to or lower than the required level
    return current_user.profile <= required_level

@categories_routes_bp.route('/', methods=['GET'])
def get_all_categories():
    db: Session = next(get_db())

    # Get the search, showHidden, and hiddenOnly parameters
    search_value = request.args.get('search', '')
    show_hidden = request.args.get('showHidden', 'false').lower() in ['true', '1']
    hidden_only = request.args.get('hiddenOnly', 'false').lower() in ['true', '1']

    # Start the query
    query = db.query(Category)

    # Filter for hidden only categories
    if hidden_only:
        query = query.filter(Category.hidden.is_(True))
    elif not show_hidden:
        # By default, show only non-hidden categories
        query = query.filter(Category.hidden.is_(False))

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
    categories_list = [{"id": category.id, "category": category.category, "hidden": category.hidden} for category in categories]
    
    return jsonify(categories_list), 200

@categories_routes_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    db: Session = next(get_db())
    
    # Get the showHidden parameter
    show_hidden = request.args.get('showHidden', 'false').lower() in ['true', '1']

    # Query the category with the given ID
    query = db.query(Category).filter(Category.id == category_id)

    # By default, don't return hidden categories unless showHidden is true
    if not show_hidden:
        query = query.filter(Category.hidden.is_(False))

    category = query.first()

    if category:
        return jsonify({
            "id": category.id,
            "category": category.category,
            "hidden": category.hidden
        }), 200
    
    return jsonify({"error": "Category not found"}), 404

@categories_routes_bp.route('/', methods=['POST'])
@jwt_required()
def create_category():
    if not check_profile_level(2):  # Only allow admin (profile <= 2) to create categories
        return jsonify({"error": "Unauthorized access"}), HTTPStatus.FORBIDDEN

    data = request.json
    try:
        category_name = data['category']  # Ensure category is provided
        
        db: Session = next(get_db())

        # Check if the category already exists
        if db.query(Category).filter(Category.category == category_name).first():
            return jsonify({"error": "Category already exists"}), HTTPStatus.BAD_REQUEST

        # Create a new category
        new_category = Category(
            category=category_name,
            hidden=False  # Default to visible
        )

        db.add(new_category)
        db.commit()
        db.refresh(new_category)

        return jsonify({
            "message": "Category created successfully", 
            "category": {
                "id": new_category.id,
                "category": new_category.category,
                "hidden": int(new_category.hidden)  # Convert boolean to int (0 or 1)
            }
        }), HTTPStatus.CREATED

    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST

@categories_routes_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    if not check_profile_level(2):  # Only allow admin (profile <= 2) to update categories
        return jsonify({"error": "Unauthorized access"}), HTTPStatus.FORBIDDEN

    data = request.json
    try:
        db: Session = next(get_db())
        
        updated_category = db.query(Category).filter(Category.id == category_id).first()
        if not updated_category:
            return jsonify({"error": "Category not found"}), HTTPStatus.NOT_FOUND

        # Update category name if provided
        if 'category' in data:
            category_name = data['category']
            if db.query(Category).filter(Category.category == category_name).first():
                return jsonify({"error": "Category already exists"}), HTTPStatus.BAD_REQUEST
            updated_category.category = category_name

        # Update hidden status if provided
        if 'hidden' in data:
            updated_category.hidden = data.get('hidden', False)

        db.commit()

        return jsonify({
            "message": "Category updated successfully", 
            "category": {
                "id": updated_category.id,
                "category": updated_category.category,
                "hidden": int(updated_category.hidden)
            }
        }), HTTPStatus.OK

    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST

@categories_routes_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    if not check_profile_level(1):  # Only allow superadmin (profile == 1) to delete categories
        return jsonify({"error": "Unauthorized access"}), HTTPStatus.FORBIDDEN

    db: Session = next(get_db())
    
    # Find the category by its ID
    category = db.query(Category).filter(Category.id == category_id).one_or_none()
    
    if not category:
        return jsonify({"error": f"Category ID {category_id} not found"}), HTTPStatus.NOT_FOUND

    # Mark the category as hidden (soft delete)
    category.hidden = True

    db.commit()

    return jsonify({"message": "Category hidden successfully", "category": {"id": category.id, "category": category.category}}), HTTPStatus.OK
