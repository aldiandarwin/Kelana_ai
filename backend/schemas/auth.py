"""Validated request and response shapes for Session 8 authentication."""

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class RegisterRequest(BaseModel):
    """New account details. Passwords are hashed before persistence."""

    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=72)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if len(normalized) < 2:
            raise ValueError("Name must contain at least 2 characters")
        return normalized

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not EMAIL_PATTERN.fullmatch(normalized):
            raise ValueError("Enter a valid email address")
        return normalized


class LoginRequest(BaseModel):
    """Credentials accepted by the JSON login endpoint."""

    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=1, max_length=72)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserResponse(BaseModel):
    """Public user fields. Password hashes never leave the backend."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    created_at: datetime


class CurrentUserResponse(UserResponse):
    """Profile payload with the user's generated trip count."""

    total_trips: int


class TokenResponse(BaseModel):
    """JWT returned after valid credentials are supplied."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
