from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from ...database import get_db, UserProfile

# Create a Blueprint for user profiles
user_profiles_routes_bp = Blueprint('user_profiles', __name__)

# Middleware to check if the user is an admin
def is_admin():
    db: Session = next(get_db())
    current_user_email = get_jwt_identity().get('email')
    current_user = db.query(User).filter(User.email == current_user_email).first()
    
    return current_user and current_user.profile < 3  # Assuming 1 represents 'superadmin' and 2 is 'admin'

@user_profiles_routes_bp.route('/', methods=['GET'])
@jwt_required()  # Require JWT authentication
def get_all_user_profiles():
    if not is_admin():
        return jsonify({"error": "Access forbidden: only admins can perform this action"}), 403

    db: Session = next(get_db())
    user_profiles = db.query(UserProfile).filter_by(hidden=False).all()
    
    return jsonify([{
        "id": up.id,
        "name": up.name,
        "hidden": up.hidden
    } for up in user_profiles]), 200


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
            "name": user_profile.name, 
            "hidden": user_profile.hidden
        }), 200
    
    return jsonify({"message": "User profile not found"}), 404

