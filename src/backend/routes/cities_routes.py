from flask import Blueprint, jsonify
from sqlalchemy.orm import Session
from ...database import get_db, City

cities_routes_bp = Blueprint('cities_routes', __name__)

@cities_routes_bp.route('/', methods=['GET'])
def get_all_cities():
    db: Session = next(get_db())

    # Fetch all cities from the database
    cities = db.query(City).all()

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
