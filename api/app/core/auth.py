import os
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from hashlib import sha256
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.app.core.database import get_db
from api.app.models.auth import AuthSession, User

ACCESS_DURATION = timedelta(minutes=15)
SESSION_DURATION = timedelta(days=7)
REFRESH_COOKIE = "itis_refresh"
COOKIE_PATH = "/api/auth"

bearer = HTTPBearer(auto_error=False)


@lru_cache
def signing_key() -> str:
    key = os.getenv("JWT_SECRET", "")
    if len(key.encode()) < 32:
        raise RuntimeError("JWT_SECRET must contain at least 32 bytes")
    return key


def refresh_digest(token: str) -> str:
    return sha256(token.encode()).hexdigest()


def issue_access_token(session: AuthSession) -> str:
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "sub": str(session.user_id),
            "sid": str(session.id),
            "iat": now,
            "exp": min(now + ACCESS_DURATION, session.expires_at),
        },
        signing_key(),
        algorithm="HS256",
    )


def unauthorized() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail="Требуется действующий вход в систему",
        headers={"WWW-Authenticate": "Bearer"},
    )


def token_session(token: str, *, verify_expiration: bool = True) -> tuple[int, UUID]:
    try:
        claims = jwt.decode(
            token,
            signing_key(),
            algorithms=["HS256"],
            options={"require": ["sub", "sid", "iat", "exp"], "verify_exp": verify_expiration},
        )
        return int(claims["sub"]), UUID(claims["sid"])
    except (jwt.InvalidTokenError, ValueError, TypeError, AttributeError):
        raise unauthorized() from None


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise unauthorized()

    user_id, session_id = token_session(credentials.credentials)
    user = db.scalar(
        select(User)
        .join(AuthSession, AuthSession.user_id == User.id)
        .where(
            User.id == user_id,
            User.is_active.is_(True),
            AuthSession.id == session_id,
            AuthSession.expires_at > datetime.now(UTC),
        )
    )
    if user is None:
        raise unauthorized()
    return user


def require_admin(user: User = Depends(current_user)) -> User:
    if user.role is None or user.role.name != "admin":
        raise HTTPException(403, "Требуются права администратора")
    return user
