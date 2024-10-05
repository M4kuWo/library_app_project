from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ...database import Base
from passlib.context import CryptContext

# Initialize the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User model for the database
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)  # Ensure email is unique
    city = Column(Integer, ForeignKey('cities.id'), nullable=False)
    age = Column(Integer, nullable=False)
    profile = Column(Integer, ForeignKey('user_profiles.id'), nullable=False)
    hidden = Column(Boolean, default=False)
    hashed_password = Column(String, nullable=False)  # Store hashed password

    # Add the relationship to the UserProfile model
    profile_relation = relationship('UserProfile', backref='users')

    # Add the relationship to the City model
    city_relation = relationship('City', backref='users')

    def __repr__(self):
        return f"<User(name={self.name}, city={self.city})>"

    # Method to hash the password
    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)

    # Method to verify the password
    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

