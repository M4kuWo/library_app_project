from flask import Blueprint, jsonify
from sqlalchemy.orm import Session
from ...database import get_db, UserProfile

# Create a Blueprint for book types
user_profiles_routes_bp = Blueprint('user_profiles', __name__)

@user_profiles_routes_bp.route('/', methods=['GET'])
def get_all_user_profiles():
    db: Session = next(get_db())
    user_profiles = db.query(UserProfile).filter_by(hidden=False).all()
    
    return jsonify([{
        "id": bt.id,  # Use the loop variable `bt`
        "name": bt.name,
        "hidden": bt.hidden
    } for bt in user_profiles]), 200


@user_profiles_routes_bp.route('/<int:user_profile_id>', methods=['GET'])
def get_user_profile(user_profile_id):
    db: Session = next(get_db())
    user_profile = db.query(UserProfile).filter_by(id=user_profile_id, hidden=False).first()
    if user_profile:
        return jsonify({
            "id": user_profile.id,
            "name": user_profile.name, 
            "hidden": user_profile.hidden
        }), 200
    return jsonify({"message": "User profile not found"}), 404
