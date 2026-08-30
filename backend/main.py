"""KelanaAI FastAPI application through Session 8.

Sessions 2-7 provide trip rules, PostgreSQL persistence, Amazon Bedrock, and the
dashboard. Session 8 adds JWT authentication and backend-owned trip ownership.
"""

import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from dependencies.auth import get_current_user
from models.trip import Trip
from models.user import User
from schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from schemas.trip import (
    TripGenerateResponse,
    TripRequest,
    TripResponse,
    TripUpdate,
)
from services.auth_service import (
    AuthConfigurationError,
    access_token_expiry_seconds,
    create_access_token,
    hash_password,
    verify_password,
)
from services.bedrock_service import BedrockError, build_prompt, generate_itinerary
from services.trip_service import calculate_daily_budget, get_trip_category

load_dotenv()

app = FastAPI(title="KelanaAI API", version="8.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importing both ORM models above registers both tables before create_all runs.
Base.metadata.create_all(bind=engine)


def _assert_session_8_schema() -> None:
    """Fail early when an older database still needs the Session 8 migration."""

    trip_columns = {column["name"] for column in inspect(engine).get_columns("trips")}
    if "user_id" not in trip_columns:
        raise RuntimeError(
            "Database ownership migration is missing. From backend/, run "
            "..\\.venv\\Scripts\\python.exe migrate_session_8.py"
        )


_assert_session_8_schema()


def _trip_for_owner(db: Session, trip_id: int, user: User) -> Trip:
    """Load a trip and enforce its owner, preserving 404 versus 403 semantics."""

    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    if trip.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this trip",
        )
    return trip


@app.get("/")
def home() -> dict[str, str]:
    """Return the KelanaAI welcome message."""

    return {"message": "Welcome to KelanaAI"}


@app.get("/health")
def health() -> dict[str, str]:
    """Return a simple public service health check."""

    return {"status": "OK"}


@app.post(
    "/api/v1/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    request: RegisterRequest,
    db: Session = Depends(get_db),
) -> User:
    """Register a unique account and store only a bcrypt password hash."""

    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    try:
        password_hash = hash_password(request.password)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    user = User(
        name=request.name,
        email=request.email,
        password_hash=password_hash,
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from error

    db.refresh(user)
    return user


@app.post("/api/v1/auth/login", response_model=TokenResponse)
def login_user(
    request: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Verify credentials and return a signed Bearer JWT."""

    user = db.query(User).filter(User.email == request.email).first()
    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        token = create_access_token(user.id)
        expires_in = access_token_expiry_seconds()
    except AuthConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication is not configured",
        ) from error

    return TokenResponse(access_token=token, expires_in=expires_in)


@app.get("/api/v1/auth/me", response_model=CurrentUserResponse)
def current_user_profile(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CurrentUserResponse:
    """Return the authenticated user's profile and owned trip count."""

    total_trips = (
        db.query(func.count(Trip.id)).filter(Trip.user_id == user.id).scalar() or 0
    )
    return CurrentUserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
        total_trips=total_trips,
    )


@app.post("/api/v1/trips", response_model=TripResponse)
def create_trip(
    request: TripRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Trip:
    """Create a trip owned by the JWT user, never a frontend-provided user id."""

    daily_budget = calculate_daily_budget(request.budget, request.days)
    category = get_trip_category(request.budget)

    trip = Trip(
        user_id=user.id,
        destination=request.destination.strip(),
        days=request.days,
        budget=request.budget,
        category=category,
        daily_budget=daily_budget,
        travel_style=request.travel_style,
    )

    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@app.get("/api/v1/trips", response_model=list[TripResponse])
def list_trips(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Trip]:
    """Return only the authenticated user's trips, newest first."""

    return (
        db.query(Trip)
        .filter(Trip.user_id == user.id)
        .order_by(Trip.created_at.desc(), Trip.id.desc())
        .all()
    )


@app.get("/api/v1/trips/{trip_id}", response_model=TripResponse)
def get_trip(
    trip_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Trip:
    """Return one owned trip; reject an existing trip owned by another user."""

    return _trip_for_owner(db, trip_id, user)


@app.put("/api/v1/trips/{trip_id}", response_model=TripResponse)
def update_trip(
    trip_id: int,
    request: TripUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Trip:
    """Update an owned trip, returning 403 for another user's trip."""

    trip = _trip_for_owner(db, trip_id, user)
    trip.budget = request.budget
    trip.daily_budget = calculate_daily_budget(request.budget, trip.days)
    trip.category = get_trip_category(request.budget)

    db.commit()
    db.refresh(trip)
    return trip


@app.delete("/api/v1/trips/{trip_id}")
def delete_trip(
    trip_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str | int]:
    """Delete an owned trip, returning 403 for another user's trip."""

    trip = _trip_for_owner(db, trip_id, user)
    db.delete(trip)
    db.commit()
    return {"deleted_id": trip_id, "status": "deleted"}


@app.post(
    "/api/v1/trips/{trip_id}/generate",
    response_model=TripGenerateResponse,
)
def generate_trip_recommendation(
    trip_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TripGenerateResponse:
    """Generate and save an itinerary only for a trip owned by the JWT user."""

    trip = _trip_for_owner(db, trip_id, user)
    prompt = build_prompt(
        destination=trip.destination,
        days=trip.days,
        budget=trip.budget,
        travel_style=trip.travel_style,
    )

    try:
        recommendation = generate_itinerary(prompt)
    except BedrockError as error:
        raise HTTPException(
            status_code=502,
            detail=f"Amazon Bedrock could not generate a recommendation: {error}",
        ) from error

    trip.ai_recommendation = recommendation
    db.commit()

    return TripGenerateResponse(
        trip_id=trip.id,
        destination=trip.destination,
        recommendation=recommendation,
    )
