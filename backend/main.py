"""Session 3: REST API for KelanaAI. Session 4: PostgreSQL persistence.

Session 5: Amazon Bedrock generates the itinerary. The Session 2 business rules
are not replaced, they run alongside it. Session 7 serves saved trips to the
multi-page dashboard.
"""

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from database import Base, SessionLocal, engine
from models.trip import Trip
from schemas.trip import (
    TripGenerateResponse,
    TripRequest,
    TripResponse,
    TripUpdate,
)
from services.bedrock_service import BedrockError, build_prompt, generate_itinerary
from services.trip_service import calculate_daily_budget, get_trip_category

load_dotenv()

app = FastAPI()

# Session 6: allow the Next.js development server to call FastAPI in the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# create the trips table from the ORM model if it does not exist yet
Base.metadata.create_all(bind=engine)


@app.get("/")
def home() -> dict[str, str]:
    """Return the KelanaAI welcome message."""

    return {"message": "Welcome to KelanaAI"}


@app.get("/health")
def health() -> dict[str, str]:
    """Return a simple service health check."""

    return {"status": "OK"}


@app.post("/api/v1/trips", response_model=TripResponse)
def create_trip(request: TripRequest) -> Trip:
    """Create a trip recommendation and save it to PostgreSQL."""

    # reuse Session 2 business logic
    daily_budget = calculate_daily_budget(request.budget, request.days)
    category = get_trip_category(request.budget)

    trip = Trip(
        destination=request.destination,
        days=request.days,
        budget=request.budget,
        category=category,
        daily_budget=daily_budget,
        travel_style=request.travel_style,
    )

    # save to PostgreSQL
    db = SessionLocal()
    db.add(trip)
    db.commit()
    db.refresh(trip)  # get the auto-generated id
    db.close()

    return trip


@app.get("/api/v1/trips", response_model=list[TripResponse])
def list_trips() -> list[Trip]:
    """Return every saved trip, newest first for the history dashboard."""

    db = SessionLocal()
    trips = db.query(Trip).order_by(Trip.created_at.desc(), Trip.id.desc()).all()
    db.close()

    return trips


@app.get("/api/v1/trips/{trip_id}", response_model=TripResponse)
def get_trip(trip_id: int) -> Trip:
    """Return one saved trip, or 404 when the id does not exist."""

    db = SessionLocal()
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    db.close()

    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")

    return trip


@app.put("/api/v1/trips/{trip_id}", response_model=TripResponse)
def update_trip(trip_id: int, request: TripUpdate) -> Trip:
    """Update the budget of a saved trip and recalculate the derived fields."""

    db = SessionLocal()
    trip = db.query(Trip).filter(Trip.id == trip_id).first()

    if trip is None:
        db.close()
        raise HTTPException(status_code=404, detail="Trip not found")

    # the business rules stay in trip_service.py, never duplicated here
    trip.budget = request.budget
    trip.daily_budget = calculate_daily_budget(request.budget, trip.days)
    trip.category = get_trip_category(request.budget)

    db.commit()
    db.refresh(trip)
    db.close()

    return trip


@app.delete("/api/v1/trips/{trip_id}")
def delete_trip(trip_id: int) -> dict[str, str | int]:
    """Remove a saved trip, or 404 when the id does not exist."""

    db = SessionLocal()
    trip = db.query(Trip).filter(Trip.id == trip_id).first()

    if trip is None:
        db.close()
        raise HTTPException(status_code=404, detail="Trip not found")

    db.delete(trip)
    db.commit()
    db.close()

    return {"deleted_id": trip_id, "status": "deleted"}


@app.post(
    "/api/v1/trips/{trip_id}/generate",
    response_model=TripGenerateResponse,
)
def generate_trip_recommendation(trip_id: int) -> TripGenerateResponse:
    """Ask Amazon Bedrock for an itinerary, store it on the trip, and return it."""

    db = SessionLocal()
    trip = db.query(Trip).filter(Trip.id == trip_id).first()

    if trip is None:
        db.close()
        raise HTTPException(status_code=404, detail="Trip not found")

    prompt = build_prompt(
        destination=trip.destination,
        days=trip.days,
        budget=trip.budget,
        travel_style=trip.travel_style,
    )

    try:
        recommendation = generate_itinerary(prompt)
    except BedrockError as error:
        # close the session on the failure path too, otherwise the connection leaks
        db.close()
        raise HTTPException(
            status_code=502,
            detail=f"Amazon Bedrock could not generate a recommendation: {error}",
        ) from error

    trip.ai_recommendation = recommendation
    db.commit()

    # build the reply before closing; commit expires the ORM attributes
    response = TripGenerateResponse(
        trip_id=trip.id,
        destination=trip.destination,
        recommendation=recommendation,
    )
    db.close()

    return response
