"""Session 4: PostgreSQL connection layer for KelanaAI."""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

# load .env so os.getenv() can read it
load_dotenv()

# connection string from .env - never hardcode secrets
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Copy .env.example to .env and fill in the password."
    )

# engine = the connection pool. Tests use one shared in-memory SQLite connection.
engine_options: dict[str, object] = {}
if DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}
    if DATABASE_URL.endswith(":memory:"):
        engine_options["poolclass"] = StaticPool

engine = create_engine(DATABASE_URL, **engine_options)

# SessionLocal = a factory for DB sessions
SessionLocal = sessionmaker(bind=engine, autoflush=False)

# Base = all ORM models inherit from this
Base = declarative_base()


def get_db():
    """Yield one database session and always close it after the request."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
