from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ...database import Base

# User model for the database
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    city = Column(Integer, ForeignKey('cities.id'), nullable=False)
    age = Column(Integer, nullable=False)
    profile = Column(Integer, ForeignKey('user_profiles.id'), nullable=False)
    hidden = Column(Boolean, default=False)

    # Add the relationship to the UserProfile model
    profile_relation = relationship('UserProfile', backref='users')

    def __repr__(self):
        return f"<User(name={self.name}, city={self.city})>"
