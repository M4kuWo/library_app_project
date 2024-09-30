from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from ...database import Base
from datetime import datetime

# Loan model for the database
class Loan(Base):
    __tablename__ = 'loans'

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    loan_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    expected_return_date = Column(DateTime, nullable=True)
    actual_return_date = Column(DateTime, nullable=True)
    hidden = Column(Boolean, default=False)

    # Relationships with Book and User models
    book = relationship("Book")
    user = relationship("User")

    def __repr__(self):
        return f"<Loan(book_id={self.book_id}, user_id={self.user_id}, loan_date={self.loan_date})>"
