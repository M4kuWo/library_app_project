from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Create an engine (for SQLite)
DATABASE_PATH = "sqlite:///src\database\library.db"
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

# Dependency to get DB session for request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize the database and create tables if they don't exist
def init_db():
    # Create all tables based on the models
    Base.metadata.create_all(bind=engine)

    # Add initial data if needed
    with Session(engine) as session:
        # Check if the table is empty
        if session.query(BookType).count() == 0:
            # Add initial book types if they don't exist
            book_types = [
                BookType(id=1, type="LONG", max_loan_duration=10),
                BookType(id=2, type="MEDIUM", max_loan_duration=5),
                BookType(id=3, type="SHORT", max_loan_duration=2)
            ]
            session.add_all(book_types)
            session.commit()

# Call init_db() to initialize the database when your application starts
if __name__ == "__main__":
    init_db()
