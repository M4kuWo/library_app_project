from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from ..models import User
from ...database import get_db, UserProfile

user_routes_bp = Blueprint('user_routes', __name__)

@user_routes_bp.route('/', methods=['POST'])
def create_user():
    data = request.json
    try:
        # Validate that the user profile exists in the UserProfile model
        user_profile_value = data['profile']  # Expecting 'profile' in the request body
        
        db: Session = next(get_db())
        
        # Query the UserProfile to check if the provided profile exists as an ID
        user_profile = db.query(UserProfile).filter(UserProfile.id == user_profile_value).first()
        
        if not user_profile:
            return jsonify({"error": "Invalid user profile ID"}), 400
        
        # Validate that the city exists
        city_id = data['city']
        city = db.query(City).filter(City.id == city_id).first()
        
        if not city:
            return jsonify({"error": "Invalid city ID"}), 400

        # Create a new user with the validated user profile and city
        new_user = User(
            name=data['name'],
            email=data['email'],
            city=city_id,  # Store the city ID
            age=data['age'],
            profile=user_profile_value,  # Use the valid user profile ID
            hidden=False
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return jsonify({"message": "User created successfully", "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "city": new_user.city,
            "age": new_user.age,
            "profile": user_profile.name,  # Send the profile name as 'profile'
            "hidden": new_user.hidden
        }}), 201

    except Exception as e:
        # Catch any general exception and return an error message
        return jsonify({"error": str(e)}), 500


@user_routes_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    db: Session = next(get_db())
    
    # Get the showHidden parameter from the request, default to False
    show_hidden = request.args.get('showHidden', 'false').lower() in ['true', '1']
    
    # Query the user with the given ID and load the related UserProfile using joinedload
    user = db.query(User).options(joinedload(User.profile_relation)).filter(User.id == user_id).first()
    
    # Check if the user exists
    if user:
        # If showHidden is False, check if the user is hidden
        if not show_hidden and user.hidden:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "city": user.city,
            "age": user.age,
            "profile": user.profile_relation.name if user.profile_relation else None,  # Return the profile name
            "hidden": user.hidden
        }), 200
    
    return jsonify({"error": "User not found"}), 404


@user_routes_bp.route('/', methods=['GET'])
def get_all_users():
    db: Session = next(get_db())
    
    # Get the showHidden parameter from the request, default to False
    show_hidden = request.args.get('showHidden', 'false').lower() in ['true', '1']
    
    # Get the hiddenOnly parameter from the request, default to None
    hidden_only = request.args.get('hiddenOnly', None)

    # Start the query
    query = db.query(User).options(joinedload(User.profile_relation))

    # Apply the showHidden logic
    if not show_hidden:
        query = query.filter(User.hidden == False)  # Only show non-hidden users by default

    # Apply hiddenOnly filter if provided
    if hidden_only in ['1', 'true']:
        query = query.filter(User.hidden == True)

    # Execute the query
    users = query.all()

    # Build the response
    users_list = [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "city": user.city,
            "age": user.age,
            "profile": user.profile_relation.name if user.profile_relation else None,  # Access the joined UserProfile
            "hidden": user.hidden
        } for user in users
    ]
    
    return jsonify(users_list), 200


@user_routes_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    db: Session = next(get_db())

    # Find the user to update
    updated_user = db.query(User).filter_by(id=user_id).first()
    if not updated_user:
        return jsonify({"error": "User not found"}), 404

    # Validate the user profile, if provided
    user_profile_value = data.get('profile')
    if user_profile_value:
        user_profile = db.query(UserProfile).filter_by(id=user_profile_value).first()
        if not user_profile:
            return jsonify({"error": "Invalid user profile ID"}), 400
        updated_user.profile = user_profile_value  # Update user profile if valid

    # Validate the city ID
    if 'city' in data:
        city_id = data['city']
        city = db.query(City).filter(City.id == city_id).first()
        if not city:
            return jsonify({"error": "Invalid city ID"}), 400
        updated_user.city = city_id  # Update the city if valid

    # Update the user fields
    updated_user.name = data.get('name', updated_user.name)
    updated_user.email = data.get('email', updated_user.email)
    updated_user.age = data.get('age', updated_user.age)
    updated_user.hidden = data.get('hidden', updated_user.hidden)

    db.commit()
    return jsonify({"message": "User updated successfully"}), 200


@user_routes_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db: Session = next(get_db())
    
    # Find the user
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Hide the user instead of deleting
    user.hidden = True  
    db.commit()
    
    return jsonify({"message": "User hidden successfully"}), 200

@user_routes_bp.route('/bulk', methods=['POST'])
def bulk_create_users():
    data = request.json
    if not isinstance(data, list):
        return jsonify({"error": "Request body must be a list of users"}), 400
    
    db: Session = next(get_db())
    created_users = []

    for user_data in data:
        # Validate that the user profile exists in the UserProfile model
        user_profile_value = user_data.get('profile')  # Expecting 'profile' in the request body
        city_value = user_data.get('city')  # Expecting 'city' in the request body

        # Query the UserProfile to check if the provided profile exists as an ID
        user_profile = db.query(UserProfile).filter(UserProfile.id == user_profile_value).first()
        if not user_profile:
            return jsonify({"error": f"Invalid user profile ID: {user_profile_value}"}), 400
        
        # Optionally validate city against cities model
        city = db.query(City).filter(City.id == city_value).first()  # Assuming you have a City model
        if not city:
            return jsonify({"error": f"Invalid city ID: {city_value}"}), 400

        # Create a new user with the validated user profile and city
        new_user = User(
            name=user_data['name'],
            email=user_data['email'],
            city=city_value,  # Use the valid city ID
            age=user_data['age'],
            profile=user_profile_value,  # Use the valid user profile ID
            hidden=False
        )

        db.add(new_user)
        created_users.append({
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "city": new_user.city,
            "age": new_user.age,
            "profile": user_profile.name,  # Send the profile name as 'profile'
            "hidden": new_user.hidden
        })

    db.commit()
    
    return jsonify({"message": "Users created successfully", "users": created_users}), 201


@user_routes_bp.route('/bulk_delete', methods=['DELETE'])
def bulk_delete_users():
    data = request.json

    # Validate the request body
    if not isinstance(data, list):
        return jsonify({"error": "Request body must be a list of user IDs"}), 400
    
    if not all(isinstance(user_id, int) for user_id in data):
        return jsonify({"error": "All user IDs must be integers"}), 400
    
    db: Session = next(get_db())

    # Query users whose IDs are in the provided list
    users_to_hide = db.query(User).filter(User.id.in_(data)).all()

    # Extract the IDs of the found users
    found_ids = {user.id for user in users_to_hide}
    
    # Determine which IDs were not found by subtracting found IDs from the provided IDs
    missing_ids = set(data) - found_ids

    # If there are missing IDs, return an error with the list of unrecognized IDs
    if missing_ids:
        return jsonify({
            "error": "Some user IDs were not recognized",
            "unrecognized_ids": list(missing_ids)
        }), 404

    # If all IDs are valid, mark the users as hidden
    for user in users_to_hide:
        user.hidden = True

    db.commit()

    return jsonify({"message": f"{len(users_to_hide)} users hidden successfully"}), 200
