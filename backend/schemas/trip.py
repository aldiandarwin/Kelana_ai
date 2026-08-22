"""Request and response shapes for the KelanaAI trip endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TripRequest(BaseModel):
    """Validated JSON body for a trip recommendation request."""

    destination: str
    days: int = Field(gt=0)
    budget: float
    # Session 5: optional, so a Session 4 request body with three fields still validates
    travel_style: str | None = None


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
    travel_style: str | None = None
    ai_recommendation: str | None = None


class TripGenerateResponse(BaseModel):
    """The reply of POST /api/v1/trips/{trip_id}/generate, shaped as the Session 5 slide."""

    trip_id: int
    destination: str
    recommendation: str
