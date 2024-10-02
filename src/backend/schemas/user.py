from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional

# UserRegistration schema for registering a new user
class UserRegistration(BaseModel):
    name: str
    email: EmailStr
    city: int
    age: int
    password: constr(min_length=8)  # Minimum length for the password

    @validator('password')
    def validate_password(cls, value: str) -> str:
        # Check for at least one uppercase letter
        if not any(char.isupper() for char in value):
            raise ValueError('Password must contain at least one uppercase letter.')
        
        # Check for at least one lowercase letter
        if not any(char.islower() for char in value):
            raise ValueError('Password must contain at least one lowercase letter.')

        # Check for at least one symbol
        if not any(char in '!@#$%^&*()-_=+[]{}|;:\'",.<>?/' for char in value):
            raise ValueError('Password must contain at least one symbol.')

        return value


# UserCreate schema for creating a new user by admin
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    city: int
    age: int
    password: constr(min_length=8)  # Minimum length for the password
    profile: int  # Field to specify the user profile

    @validator('password')
    def validate_password(cls, value: str) -> str:
        # Check for at least one uppercase letter
        if not any(char.isupper() for char in value):
            raise ValueError('Password must contain at least one uppercase letter.')
        
        # Check for at least one lowercase letter
        if not any(char.islower() for char in value):
            raise ValueError('Password must contain at least one lowercase letter.')

        # Check for at least one symbol
        if not any(char in '!@#$%^&*()-_=+[]{}|;:\'",.<>?/' for char in value):
            raise ValueError('Password must contain at least one symbol.')

        return value


# Optional schema for user response
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    city: int
    age: int

    class Config:
        orm_mode = True  # Enable ORM mode for SQLAlchemy compatibility
