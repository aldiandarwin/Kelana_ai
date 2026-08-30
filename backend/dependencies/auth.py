"""FastAPI dependency that resolves the current user from a Bearer JWT."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from services.auth_service import InvalidTokenError, decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Return the database user identified by a valid Bearer token."""

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized()

    try:
        user_id = decode_access_token(credentials.credentials)
    except InvalidTokenError as error:
        raise _unauthorized() from error

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise _unauthorized()
    return user
