import json
import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Create an engine (for SQLite)
DATABASE_PATH = "sqlite:///src/database/library.db"
engine = create_engine(DATABASE_PATH, echo=True)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

# Define the ORM model for book_types
class BookType(Base):
    __tablename__ = "book_types"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    max_loan_duration = Column(Integer, nullable=False)
    hidden = Column(Boolean, default=False)

# Define the ORM model for user_profiles
class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    hidden = Column(Boolean, default=False)

# Define the ORM model for cities
class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    hidden = Column(Boolean, default=False)

# Dependency to get DB session for request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to load cities from a JSON file
def load_cities_from_json():
    json_file_path = os.path.join(os.path.dirname(__file__), 'cities.json')
    with open(json_file_path, 'r', encoding='utf-8') as f:
        cities_data = json.load(f)
    return cities_data

# Initialize the database and create tables if they don't exist
def init_db():
    # Create all tables based on the models
    Base.metadata.create_all(bind=engine)

    # Add initial data if needed
    with Session(engine) as session:
        # Initialize book types if the table is empty
        if session.query(BookType).count() == 0:
            book_types = [
                BookType(id=1, type="LONG", max_loan_duration=10),
                BookType(id=2, type="MEDIUM", max_loan_duration=5),
                BookType(id=3, type="SHORT", max_loan_duration=2)
            ]
            session.add_all(book_types)

        # Initialize user profiles if the table is empty
        if session.query(UserProfile).count() == 0:
            user_profiles = [
                UserProfile(id=1, name="admin", hidden=False),
                UserProfile(id=2, name="user", hidden=False)
            ]
            session.add_all(user_profiles)

        # Initialize cities if the table is empty
        if session.query(City).count() == 0:
            cities_data = load_cities_from_json()
            cities = [City(id=city['id'], name=city['name']) for city in cities_data]
            session.add_all(cities)

        session.commit()

# Call init_db() to initialize the database when your application starts
if __name__ == "__main__":
    init_db()
