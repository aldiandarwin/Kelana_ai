"""Session 4: the Trip ORM model. A Python class becomes a database table."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String

from database import Base


def _utc_now() -> datetime:
    """Return the current UTC time. Replaces the deprecated datetime.utcnow."""

    return datetime.now(timezone.utc)


class Trip(Base):
    """One saved trip recommendation."""

    __tablename__ = "trips"

    id = Column(Integer, primary_key=True)
    destination = Column(String, nullable=False)
    days = Column(Integer, nullable=False)
    budget = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    daily_budget = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now)
