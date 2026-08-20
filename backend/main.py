"""Session 3: REST API for KelanaAI. Session 4: PostgreSQL persistence."""

from fastapi import FastAPI, HTTPException

from database import Base, SessionLocal, engine
from models.trip import Trip
from schemas.trip import TripRequest, TripResponse, TripUpdate
from services.trip_service import calculate_daily_budget, get_trip_category

app = FastAPI()

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
    """Return every saved trip."""

    db = SessionLocal()
    trips = db.query(Trip).all()
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
