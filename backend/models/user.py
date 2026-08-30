"""Session 8: authenticated KelanaAI user model."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from database import Base


def _utc_now() -> datetime:
    """Return the current UTC time for new users."""

    return datetime.now(timezone.utc)


class User(Base):
    """One account that owns zero or more trips."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now)

    trips = relationship("Trip", back_populates="owner")
