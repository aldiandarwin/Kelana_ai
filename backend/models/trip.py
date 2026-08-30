"""Session 4: the Trip ORM model. A Python class becomes a database table."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


def _utc_now() -> datetime:
    """Return the current UTC time. Replaces the deprecated datetime.utcnow."""

    return datetime.now(timezone.utc)


class Trip(Base):
    """One saved trip recommendation."""

    __tablename__ = "trips"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    destination = Column(String, nullable=False)
    days = Column(Integer, nullable=False)
    budget = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    daily_budget = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now)

    # Session 5: both are nullable because trips saved in Session 4 predate them
    travel_style = Column(String, nullable=True)
    # Text, not String: an AI itinerary has no length we can predict
    ai_recommendation = Column(Text, nullable=True)

    owner = relationship("User", back_populates="trips")
