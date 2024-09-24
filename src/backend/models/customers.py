from sqlalchemy import Column, Integer, String, Boolean
from ...database import Base

# Customer model for the database
class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    hidden = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Customer(name={self.name}, city={self.city})>"
