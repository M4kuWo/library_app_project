from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ...database import Base

# Book model for the database
class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    category = Column(Integer, ForeignKey('categories.id'), nullable=False)
    cover_image = Column(String, nullable=True)
    year_published = Column(Integer, nullable=False)
    number_of_pages = Column(Integer, nullable=False)
    book_type_id = Column(Integer, ForeignKey('book_types.id'), nullable=False)
    hidden = Column(Boolean, default=False)

    # Relationship with BookType model
    book_type = relationship("BookType")

    # Relationship with categories model
    book_type = relationship("Category")


    def __repr__(self):
        return f"<Book(title={self.title}, author={self.author})>"
