from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .models import User  # Import your User model
from ..database import get_db  # Function to get database session
from .schemas.user import UserResponse  # Import your UserResponse schema

# Dependency to get the current user
def get_current_user(token: str, db: Session = Depends(get_db)) -> User:
    # Logic to decode the token and retrieve the user
    user = db.query(User).filter(User.token == token).first()  # Example logic
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return user

# Dependency to check if the user is an admin
def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.profile != 1:  # Assuming 1 is the admin profile ID
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user
