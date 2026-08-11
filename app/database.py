"""Database configuration: engine, session factory, Base, and FastAPI dependency."""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load variables from the .env file in the project root (if present).
load_dotenv()

# Read the full PostgreSQL connection string from .env.
# Example:
#   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/url_shortener
DATABASE_URL = os.getenv("DATABASE_URL")

# The engine is the entry point for all database communication.
# It knows the database type, location, and credentials.
engine = create_engine(DATABASE_URL)

# SessionLocal is a factory that creates database sessions.
# A session is a conversation with the database: you use it to query,
# add, and commit changes. autoflush=False gives us control over when
# statements are sent.
SessionLocal = sessionmaker(bind=engine, autoflush=False)

# Base is the declarative base class. Every SQLAlchemy model inherits
# from it, and it keeps track of all models so tables can be created.
Base = declarative_base()


def get_db():
    """FastAPI dependency that provides a database session per request.

    The session is automatically closed when the request finishes,
    even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
