from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from ..models import User
from ...database import get_db

user_routes_bp = Blueprint('user_routes', __name__)

@user_routes_bp.route('/', methods=['POST'])
def create_user():
    data = request.json
    new_user = User(
        id=None,
        name=data['name'],
        city=data['city'],
        age=data['age'],
        hidden=False
    )
    db: Session = next(get_db())
    db.add(new_user)
    db.commit()
    return jsonify({"message": "User created successfully"}), 201

@user_routes_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    db: Session = next(get_db())
    user = db.query(User).filter_by(id=user_id, hidden=False).first()
    if user:
        return jsonify({
            "id": user.id,
            "name": user.name,
            "city": user.city,
            "age": user.age,
            "hidden": user.hidden
        }), 200
    return jsonify({"error": "User not found"}), 404

@user_routes_bp.route('/', methods=['GET'])
def get_all_users():
    db: Session = next(get_db())
    users = db.query(User).filter_by(hidden=False).all()
    return jsonify([{
        "id": user.id,
        "name": user.name,
        "city": user.city,
        "age": user.age,
        "hidden": user.hidden
    } for user in users]), 200

@user_routes_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    db: Session = next(get_db())
    updated_user = db.query(User).filter_by(id=user_id).first()
    if updated_user:
        updated_user.name = data['name']
        updated_user.city = data['city']
        updated_user.age = data['age']
        updated_user.hidden = data.get('hidden', False)
        db.commit()
        return jsonify({"message": "User updated successfully"}), 200
    return jsonify({"error": "User not found"}), 404

@user_routes_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db: Session = next(get_db())
    user = db.query(user).filter_by(id=user_id).first()
    if user:
        user.hidden = True  # Hide the user instead of deleting
        db.commit()
        return jsonify({"message": "User hidden successfully"}), 200
    return jsonify({"error": "User not found"}), 404
