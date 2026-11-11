"""Database configuration and session management module."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Default to SQLite if DATABASE_URL is not set in environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///recipes.db")

# Configure engine (handle SQLite specific thread check if needed)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency generator that yields a database session per request,
    ensuring it is closed safely after the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
