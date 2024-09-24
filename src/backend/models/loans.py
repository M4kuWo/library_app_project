from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from ...database import Base
from datetime import datetime

# Loan model for the database
class Loan(Base):
    __tablename__ = 'loans'

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    loan_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    return_date = Column(DateTime, nullable=True)
    hidden = Column(Boolean, default=False)

    # Relationships with Book and Customer models
    book = relationship("Book")
    customer = relationship("Customer")

    def __repr__(self):
        return f"<Loan(book_id={self.book_id}, customer_id={self.customer_id}, loan_date={self.loan_date})>"
