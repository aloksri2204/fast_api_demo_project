"""SQLAlchemy ORM models used by the application."""

from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Product(Base):
    """Persisted product entity stored in the PostgreSQL database."""

    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    desc = Column(String)
    price = Column(Float)
    quantity = Column(Integer)
