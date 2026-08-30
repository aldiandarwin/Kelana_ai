"""Password hashing and JWT helpers for Session 8 authentication."""

import os
from datetime import datetime, timedelta, timezone

import bcrypt
from dotenv import load_dotenv
from jose import JWTError, jwt

load_dotenv()

JWT_ALGORITHM = "HS256"
DEFAULT_ACCESS_TOKEN_MINUTES = 480


class AuthConfigurationError(RuntimeError):
    """Raised when a required authentication setting is missing or unsafe."""


class InvalidTokenError(ValueError):
    """Raised when a JWT cannot identify a valid KelanaAI user."""


def _jwt_secret_key() -> str:
    secret = os.getenv("JWT_SECRET_KEY", "")
    if len(secret) < 32 or secret.startswith(("YOUR_", "GENERATE_")):
        raise AuthConfigurationError(
            "JWT_SECRET_KEY must be set to a random value of at least 32 characters."
        )
    return secret


def access_token_expiry_seconds() -> int:
    """Return the configured JWT lifetime in seconds."""

    raw_minutes = os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        str(DEFAULT_ACCESS_TOKEN_MINUTES),
    )
    try:
        minutes = int(raw_minutes)
    except ValueError as error:
        raise AuthConfigurationError(
            "ACCESS_TOKEN_EXPIRE_MINUTES must be a positive integer."
        ) from error

    if minutes <= 0:
        raise AuthConfigurationError(
            "ACCESS_TOKEN_EXPIRE_MINUTES must be a positive integer."
        )
    return minutes * 60


def hash_password(password: str) -> str:
    """Hash a password with bcrypt. Plain text is never persisted."""

    encoded = password.encode("utf-8")
    if len(encoded) > 72:
        raise ValueError("Password must be at most 72 UTF-8 bytes")
    return bcrypt.hashpw(encoded, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Safely compare a plain password with a stored bcrypt hash."""

    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (TypeError, ValueError):
        return False


def create_access_token(user_id: int) -> str:
    """Sign a short-lived JWT whose subject is the authenticated user id."""

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(seconds=access_token_expiry_seconds())
    return jwt.encode(
        {
            "sub": str(user_id),
            "iat": now,
            "exp": expires_at,
        },
        _jwt_secret_key(),
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> int:
    """Verify a JWT and return its user id subject."""

    try:
        payload = jwt.decode(
            token,
            _jwt_secret_key(),
            algorithms=[JWT_ALGORITHM],
        )
        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject.isdigit():
            raise InvalidTokenError("Token subject is invalid")
        return int(subject)
    except (JWTError, AuthConfigurationError) as error:
        if isinstance(error, AuthConfigurationError):
            raise
        raise InvalidTokenError("Token is invalid or expired") from error
