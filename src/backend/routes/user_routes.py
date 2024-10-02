from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from sqlalchemy.orm import Session, joinedload
from ...database import get_db, UserProfile, City
from ..models import User
from ..schemas.user import UserCreate, UserResponse
from ..dependencies import get_current_admin, get_current_user
from passlib.context import CryptContext
from http import HTTPStatus
from pydantic import ValidationError

user_routes_bp = Blueprint('user_routes', __name__)

# Create a new SQLAlchemy instance with a different variable name
database = SQLAlchemy()

# Initialize the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# New registration route with password hashing
@user_routes_bp.route('/register', methods=['POST'])
def register_user():
    data = request.json
    try:
        db: Session = next(get_db())
        
        # Automatically assign the "user" profile (profile_id=2)
        default_user_profile_id = 3
        
        # Validate that the city exists
        city_id = data['city']
        city = db.query(City).filter(City.id == city_id).first()
        
        if not city:
            return jsonify({"error": "Invalid city ID"}), HTTPStatus.BAD_REQUEST

        # Create a new user instance
        new_user = User(
            name=data['name'],
            email=data['email'],
            city=city_id,  # Store the city ID
            age=data['age'],
            profile=default_user_profile_id,  # Assign the default "user" profile
            hidden=False
        )

        # Hash the password using the User model's set_password method
        new_user.set_password(data['password'])

        # Add and commit the new user to the database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return jsonify({"message": "User registered successfully", "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "city": new_user.city,
            "age": new_user.age,
            "profile": "User",  # Returning the default profile name
            "hidden": new_user.hidden
        }}), HTTPStatus.CREATED

    except Exception as e:
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@user_routes_bp.route('/create_user', methods=['POST'])
@jwt_required()  # Protect the route with JWT
def create_user():
    # Get the current user's identity (email or ID)
    current_user_email = get_jwt_identity().get('email')

    # Fetch the current user from the database to check for admin privileges
    db: Session = next(get_db())
    current_user = db.query(User).filter(User.email == current_user_email).first()

    if not current_user:
        return jsonify({"error": "User not found"}), HTTPStatus.UNAUTHORIZED

    # Check if the current user is an admin
    if current_user.profile > 2 :  # Assuming 'profile' field determines if user is an admin
        return jsonify({"error": "Permission denied. Admins only."}), HTTPStatus.FORBIDDEN

    # Validate incoming request data using the UserCreate schema
    user_data = request.json
    try:
        user_create = UserCreate(**user_data)  # Validate and create a UserCreate instance
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST

    # Check if the email is already registered
    existing_user = db.query(User).filter(User.email == user_create.email).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), HTTPStatus.BAD_REQUEST

    # Create a new user instance with the specified profile
    new_user = User(
        name=user_create.name,
        email=user_create.email,
        city=user_create.city,
        age=user_create.age,
        profile=user_create.profile  # Use the profile from the request (e.g., user/admin)
    )
    new_user.set_password(user_create.password)  # Hash the password

    # Add the user to the database
    db.add(new_user)
    db.commit()

    # Prepare the user response
    user_response = UserResponse(
        id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        city=new_user.city,
        age=new_user.age
    )

    return jsonify(user_response.dict()), HTTPStatus.CREATED

@user_routes_bp.route('/bulk', methods=['POST'])
@jwt_required()
def bulk_create_users():
    data = request.json
    if not isinstance(data, list):
        return jsonify({"error": "Request body must be a list of users"}), HTTPStatus.BAD_REQUEST
    
    db: Session = next(get_db())
    
    # Get the current user's email from the JWT token
    current_user_email = get_jwt_identity().get('email')
    
    # Find the current user based on the email
    current_user = db.query(User).filter(User.email == current_user_email).first()

    # Check if the current user exists and if they are an admin
    if not current_user or current_user.profile > 2:  # Assuming 'profile' determines the role
        return jsonify({"error": "Access forbidden: only admins can perform this action"}), HTTPStatus.FORBIDDEN

    created_users = []
    symbols = "!@#$%^&*(),.?\":{}|<>"

    for user_data in data:
        # Use the UserCreate schema to validate and parse the input data
        try:
            user_schema = UserCreate(**user_data)  # Validate and parse user data
        except ValidationError as e:
            return jsonify({"error": f"Validation error for user '{user_data.get('email', 'unknown')}': {e.errors()}"}), HTTPStatus.BAD_REQUEST
        
        # Manual password validation for required characteristics
        password = user_schema.password
        if len(password) < 8:
            return jsonify({"error": f"Password for user '{user_schema.email}' must be at least 8 characters long."}), HTTPStatus.BAD_REQUEST
        if not any(char in symbols for char in password):
            return jsonify({"error": f"Password for user '{user_schema.email}' must contain at least one symbol."}), HTTPStatus.BAD_REQUEST
        if not any(char.isdigit() for char in password):
            return jsonify({"error": f"Password for user '{user_schema.email}' must contain at least one digit."}), HTTPStatus.BAD_REQUEST
        if not any(char.islower() for char in password):
            return jsonify({"error": f"Password for user '{user_schema.email}' must contain at least one lowercase letter."}), HTTPStatus.BAD_REQUEST
        if not any(char.isupper() for char in password):
            return jsonify({"error": f"Password for user '{user_schema.email}' must contain at least one uppercase letter."}), HTTPStatus.BAD_REQUEST
        
        # Validate that the user profile exists in the UserProfile model
        user_profile_value = user_schema.profile  # Use parsed profile value
        city_value = user_schema.city  # Use parsed city value

        # Query the UserProfile to check if the provided profile exists as an ID
        user_profile = db.query(UserProfile).filter(UserProfile.id == user_profile_value).first()
        if not user_profile:
            return jsonify({"error": f"Invalid user profile ID: {user_profile_value}"}), HTTPStatus.BAD_REQUEST
        
        # Optionally validate city against cities model
        city = db.query(City).filter(City.id == city_value).first()  # Assuming you have a City model
        if not city:
            return jsonify({"error": f"Invalid city ID: {city_value}"}), HTTPStatus.BAD_REQUEST

        # Hash the validated password
        hashed_password = pwd_context.hash(user_schema.password)

        # Create a new user with the validated user profile, city, and hashed password
        new_user = User(
            name=user_schema.name,
            email=user_schema.email,
            city=city_value,  # Use the valid city ID
            age=user_schema.age,
            profile=user_profile_value,  # Use the valid user profile ID
            hidden=False,  # Set hidden to False
            hashed_password=hashed_password  # Use the hashed password here
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
    
    return jsonify({"message": "Users created successfully", "users": created_users}), HTTPStatus.CREATED

@user_routes_bp.route('/login', methods=['POST'])
def login_user():
    data = request.json
    db: Session = next(get_db())

    # Find the user by email
    user = db.query(User).filter(User.email == data['email']).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if the provided password matches the stored hash
    password = data['password']
    if user.verify_password(password):
        # Create a token with the user information (e.g., id, profile)
        access_token = create_access_token(
            identity={
                "id": user.id,
                "email": user.email,
                "profile": "User" if user.profile == 2 else "Admin"
            },
            expires_delta=timedelta(hours=1)  # Token expiration time
        )
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "profile": "User" if user.profile == 2 else "Admin"
            }
        }), 200
    else:
        return jsonify({"error": "Invalid password"}), 401

@user_routes_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    db: Session = next(get_db())

    # Get the current user's email from the JWT token
    current_user_email = get_jwt_identity().get('email')

    # Find the current user based on the email
    current_user = db.query(User).filter(User.email == current_user_email).first()

    # Check if current user exists and if they are an admin (profile = 1)
    if not current_user or current_user.profile > 2:  # Assuming 1 represents 'Admin'
        return jsonify({"error": "Access forbidden: only admins can perform this action"}), 403

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
@jwt_required()
def get_all_users():
    db: Session = next(get_db())
    
    # Get the showHidden parameter from the request, default to False
    show_hidden = request.args.get('showHidden', 'false').lower() in ['true', '1']
    
    # Get the hiddenOnly parameter from the request, default to None
    hidden_only = request.args.get('hiddenOnly', None)

    # Get the current user's email from the JWT token
    current_user_email = get_jwt_identity().get('email')
    
    # Find the current user based on the email
    current_user = db.query(User).filter(User.email == current_user_email).first()

    # Check if current user exists and if they are an admin
    if not current_user or current_user.profile > 2:  # Assuming 'profile' determines the role
        return jsonify({"error": "Access forbidden: only admins can perform this action"}), 403

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
@jwt_required()
def update_user(user_id):
    data = request.json
    db: Session = next(get_db())

    # Get the current user's email from the JWT token
    current_user_email = get_jwt_identity().get('email')

    # Find the current user based on the email
    current_user = db.query(User).filter(User.email == current_user_email).first()

    # Check if current user exists and if they are an admin
    if not current_user or current_user.profile > 2:  # Assuming 'profile' determines the role
        return jsonify({"error": "Access forbidden: only admins can perform this action"}), 403

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
@jwt_required()
def delete_user(user_id):
    db: Session = next(get_db())

    # Get the current user's email from the JWT token
    current_user_email = get_jwt_identity().get('email')

    # Find the current user based on the email
    current_user = db.query(User).filter(User.email == current_user_email).first()

    # Check if current user exists and if they are an admin
    if not current_user or current_user.profile > 2:  # Assuming 'profile' determines the role
        return jsonify({"error": "Access forbidden: only admins can perform this action"}), 403

    # Find the user to be hidden
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Hide the user instead of deleting
    user.hidden = True  
    db.commit()
    
    return jsonify({"message": "User hidden successfully"}), 200

@user_routes_bp.route('/bulk_delete', methods=['DELETE'])
@jwt_required()
def bulk_delete_users():
    data = request.json

    # Validate the request body
    if not isinstance(data, list):
        return jsonify({"error": "Request body must be a list of user IDs"}), 400
    
    if not all(isinstance(user_id, int) for user_id in data):
        return jsonify({"error": "All user IDs must be integers"}), 400
    
    db: Session = next(get_db())

    # Get the current user's email from the JWT token
    current_user_email = get_jwt_identity().get('email')
    
    # Find the current user based on the email
    current_user = db.query(User).filter(User.email == current_user_email).first()

    # Check if the current user exists and if they are an admin
    if not current_user or current_user.profile > 2:  # Assuming 'profile' determines the role
        return jsonify({"error": "Access forbidden: only admins can perform this action"}), 403

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
