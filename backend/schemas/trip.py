"""Request and response shapes for the KelanaAI trip endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TripRequest(BaseModel):
    """Validated JSON body for a trip recommendation request."""

    destination: str
    days: int = Field(gt=0)
    budget: float


class TripUpdate(BaseModel):
    """Validated JSON body for updating the budget of a saved trip."""

    budget: float


class TripResponse(BaseModel):
    """A saved trip, serialised straight from the ORM object."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    destination: str
    days: int
    budget: float
    daily_budget: float
    category: str
    created_at: datetime
