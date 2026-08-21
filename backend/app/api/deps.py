import uuid

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import UnauthorizedError
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user_repo import UserRepository


def get_current_user(
    authorization: str | None = Header(default=None), db: Session = Depends(get_db)
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing or invalid authorization header")
    token = authorization.split(" ", 1)[1]
    subject = decode_access_token(token)
    if not subject:
        raise UnauthorizedError("Invalid or expired token")
    user = UserRepository(db).get_by_id(uuid.UUID(subject))
    if not user:
        raise UnauthorizedError("User not found")
    return user
