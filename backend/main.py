"""Session 3: REST API for KelanaAI."""

from fastapi import FastAPI
from pydantic import BaseModel, Field

from services.trip_service import calculate_daily_budget, get_trip_category

app = FastAPI()


class TripRequest(BaseModel):
    """Validated JSON body for a trip recommendation request."""

    destination: str
    days: int = Field(gt=0)
    budget: float


@app.get("/")
def home() -> dict[str, str]:
    """Return the KelanaAI welcome message."""

    return {"message": "Welcome to KelanaAI"}


@app.get("/health")
def health() -> dict[str, str]:
    """Return a simple service health check."""

    return {"status": "OK"}


@app.post("/api/v1/trips")
def create_trip(request: TripRequest) -> dict[str, str | int | float]:
    """Create a trip recommendation using the Session 2 business rules."""

    daily_budget = calculate_daily_budget(request.budget, request.days)
    category = get_trip_category(request.budget)

    return {
        "destination": request.destination,
        "days": request.days,
        "budget": request.budget,
        "daily_budget": daily_budget,
        "category": category,
    }
