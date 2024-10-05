from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session
from sqlalchemy import or_  # Importing `or_` for filtering queries
from ...database import get_db, City

cities_routes_bp = Blueprint('cities_routes', __name__)

@cities_routes_bp.route('/', methods=['GET'])
def get_all_cities():
    db: Session = next(get_db())

    # Get the search parameter for name or ID
    search_value = request.args.get('search', '')

    # Start the query
    query = db.query(City)

    # Add search functionality for name or ID (case insensitive)
    if search_value:
        search_pattern = f"%{search_value}%"
        query = query.filter(
            or_(
                City.name.ilike(search_pattern),  # Search by name
                City.id.ilike(search_pattern)     # Search by ID
            )
        )

    # Fetch cities based on the query
    cities = query.all()

    # Build the response
    cities_list = [{"id": city.id, "name": city.name} for city in cities]
    
    return jsonify(cities_list), 200

@cities_routes_bp.route('/<int:city_id>', methods=['GET'])
def get_city(city_id):
    db: Session = next(get_db())
    
    # Query the city with the given ID
    city = db.query(City).filter(City.id == city_id).first()

    if city:
        return jsonify({
            "id": city.id,
            "name": city.name
        }), 200
    
    return jsonify({"error": "City not found"}), 404
