from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from sqlalchemy import or_  # Importing `or_` for filtering queries
from ...database import get_db, UserProfile

# Create a Blueprint for user profiles
user_profiles_routes_bp = Blueprint('user_profiles', __name__)

# Middleware to check if the user is an admin
def is_admin():
    # Get the current user's profile from the JWT token
    current_user_profile = get_jwt_identity().get('profile')
    return current_user_profile < 3  # Assuming 1 and 2 represent 'admin' profiles

@user_profiles_routes_bp.route('/', methods=['GET'])
@jwt_required()  # Require JWT authentication
def get_all_user_profiles():
    if not is_admin():
        return jsonify({"error": "Access forbidden: only admins can perform this action"}), 403

    db: Session = next(get_db())

    # Get search parameter for name or ID
    search_value = request.args.get('search', '')

    # Start the query, filtering out hidden profiles
    query = db.query(UserProfile).filter_by(hidden=False)

    # Add search functionality for name or ID (case insensitive)
    if search_value:
        search_pattern = f"%{search_value}%"
        query = query.filter(
            or_(
                UserProfile.name.ilike(search_pattern),  # Search by name
                UserProfile.id.ilike(search_pattern)     # Search by ID
            )
        )

    # Execute the query
    user_profiles = query.all()

    # Build the response
    user_profiles_list = [{
        "id": up.id,
        "name": up.name,  # Include name
        "hidden": up.hidden
    } for up in user_profiles]

    return jsonify(user_profiles_list), 200

@user_profiles_routes_bp.route('/<int:user_profile_id>', methods=['GET'])
@jwt_required()  # Require JWT authentication
def get_user_profile(user_profile_id):
    if not is_admin():
        return jsonify({"error": "Access forbidden: only admins can perform this action"}), 403

    db: Session = next(get_db())
    user_profile = db.query(UserProfile).filter_by(id=user_profile_id, hidden=False).first()
    
    if user_profile:
        return jsonify({
            "id": user_profile.id,
            "name": user_profile.name,  # Include name
            "hidden": user_profile.hidden
        }), 200
    
    return jsonify({"message": "User profile not found"}), 404
