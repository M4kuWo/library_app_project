from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from ..models import Customer
from ...database import get_db

customer_routes_bp = Blueprint('customer_routes', __name__)

@customer_routes_bp.route('/', methods=['POST'])
def create_customer():
    data = request.json
    new_customer = Customer(
        id=None,
        name=data['name'],
        city=data['city'],
        age=data['age'],
        hidden=False
    )
    db: Session = next(get_db())
    db.add(new_customer)
    db.commit()
    return jsonify({"message": "Customer created successfully"}), 201

@customer_routes_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    db: Session = next(get_db())
    customer = db.query(Customer).filter_by(id=customer_id, hidden=False).first()
    if customer:
        return jsonify({
            "id": customer.id,
            "name": customer.name,
            "city": customer.city,
            "age": customer.age,
            "hidden": customer.hidden
        }), 200
    return jsonify({"error": "Customer not found"}), 404

@customer_routes_bp.route('/', methods=['GET'])
def get_all_customers():
    db: Session = next(get_db())
    customers = db.query(Customer).filter_by(hidden=False).all()
    return jsonify([{
        "id": customer.id,
        "name": customer.name,
        "city": customer.city,
        "age": customer.age,
        "hidden": customer.hidden
    } for customer in customers]), 200

@customer_routes_bp.route('/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    data = request.json
    db: Session = next(get_db())
    updated_customer = db.query(Customer).filter_by(id=customer_id).first()
    if updated_customer:
        updated_customer.name = data['name']
        updated_customer.city = data['city']
        updated_customer.age = data['age']
        updated_customer.hidden = data.get('hidden', False)
        db.commit()
        return jsonify({"message": "Customer updated successfully"}), 200
    return jsonify({"error": "Customer not found"}), 404

@customer_routes_bp.route('/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    db: Session = next(get_db())
    customer = db.query(Customer).filter_by(id=customer_id).first()
    if customer:
        customer.hidden = True  # Hide the customer instead of deleting
        db.commit()
        return jsonify({"message": "Customer hidden successfully"}), 200
    return jsonify({"error": "Customer not found"}), 404
