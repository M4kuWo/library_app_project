# from sqlalchemy import Column, Integer, String, Boolean
from ...database import Base

# Might not even need this shit

# BookType model for the database
# class BookType(Base):
#     __tablename__ = 'book_types'

#     id = Column(Integer, primary_key=True, index=True)
#     type = Column(String, nullable=False)  
#     max_loan_duration = Column(Integer, nullable=False) 
#     hidden = Column(Boolean, default=False)  

#     def __repr__(self):
#         return f"<BookType(type={self.type}, max_loan_duration={self.max_loan_duration})>"
