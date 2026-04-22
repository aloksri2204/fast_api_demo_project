"""Database engine and session factory configuration."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Use environment variable for database URL, fallback to the local standalone setup.
db_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/fastapi_db")

engine = create_engine(db_url)
session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
