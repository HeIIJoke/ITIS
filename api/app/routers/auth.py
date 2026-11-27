import os
import secrets
from datetime import UTC, datetime
from typing import Annotated, Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.security import HTTPAuthorizationCredentials
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError
from pydantic import BaseModel, ConfigDict, SecretStr, StringConstraints
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from api.app.core.auth import (
    COOKIE_PATH,
    REFRESH_COOKIE,
    SESSION_DURATION,
    bearer,
    current_user,
    issue_access_token,
    refresh_digest,
    require_admin,
    token_session,
    unauthorized,
)
from api.app.core.database import get_db
from api.app.models.auth import AuthSession, Role, User

Login = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50, pattern=r"^[^\x00]+$")]
NewLogin = Annotated[Login, StringConstraints(min_length=3)]
AssignableRole = Literal["guest", "student", "teacher"]

password_hash = PasswordHash.recommended()
dummy_hash = password_hash.hash(secrets.token_urlsafe(32))


class Credentials(BaseModel):
    model_config = ConfigDict(extra="forbid")

    login: Login
    password: Annotated[SecretStr, StringConstraints(min_length=1, max_length=1024)]


class Account(BaseModel):
    login: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class RoleChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: AssignableRole


def account(user: User) -> Account:
    return Account(login=user.login, role=user.role.name if user.role else "guest")


def same_origin(request: Request) -> None:
    origin = request.headers.get("origin")
    expected = os.getenv("AUTH_ORIGIN") or f"{request.url.scheme}://{request.url.netloc}"
    if origin is not None and origin != expected:
        raise HTTPException(403, "Запрос с другого сайта отклонён")


def secure_cookie() -> bool:
    return os.getenv("AUTH_COOKIE_SECURE", "true").lower() != "false"


router = APIRouter(prefix="/api/auth", tags=["Авторизация"], dependencies=[Depends(same_origin)])
admin_router = APIRouter(
    prefix="/api/admin/users", tags=["Пользователи"], dependencies=[Depends(require_admin)]
)


@router.post("/login")
def login(body: Credentials, response: Response, db: Session = Depends(get_db)) -> Token:
    user = db.scalar(select(User).where(User.login == body.login))
    try:
        valid = password_hash.verify(body.password.get_secret_value(), user.password_hash if user else dummy_hash)
    except (UnknownHashError, ValueError):
        valid = False
    if not valid or user is None or not user.is_active:
        raise HTTPException(401, "Неверный логин или пароль")

    now = datetime.now(UTC)
    db.execute(delete(AuthSession).where(AuthSession.expires_at <= now))
    refresh_token = secrets.token_urlsafe(32)
    session = AuthSession(
        id=uuid4(),
        user_id=user.id,
        refresh_token_hash=refresh_digest(refresh_token),
        expires_at=now + SESSION_DURATION,
    )
    db.add(session)
    access_token = issue_access_token(session)
    db.commit()

    response.set_cookie(
        REFRESH_COOKIE,
        refresh_token,
        max_age=int(SESSION_DURATION.total_seconds()),
        path=COOKIE_PATH,
        httponly=True,
        secure=secure_cookie(),
        samesite="strict",
    )
    return Token(access_token=access_token)


@router.post("/refresh")
def refresh(request: Request, db: Session = Depends(get_db)) -> Token:
    token = request.cookies.get(REFRESH_COOKIE)
    if not token:
        raise unauthorized()
    session = db.scalar(
        select(AuthSession)
        .join(User, AuthSession.user_id == User.id)
        .where(
            AuthSession.refresh_token_hash == refresh_digest(token),
            AuthSession.expires_at > datetime.now(UTC),
            User.is_active.is_(True),
        )
    )
    if session is None:
        raise unauthorized()
    return Token(access_token=issue_access_token(session))


@router.post("/logout", status_code=204)
def logout(
    request: Request,
    response: Response,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> None:
    token = request.cookies.get(REFRESH_COOKIE)
    cookie_digest = refresh_digest(token) if token else None
    revoke = delete(AuthSession).returning(AuthSession.refresh_token_hash)
    revoked_digest = None
    if credentials:
        user_id, session_id = token_session(credentials.credentials, verify_expiration=False)
        revoked_digest = db.scalar(revoke.where(AuthSession.id == session_id, AuthSession.user_id == user_id))
        db.commit()
    elif cookie_digest:
        db.execute(revoke.where(AuthSession.refresh_token_hash == cookie_digest))
        db.commit()

    if credentials is None or revoked_digest == cookie_digest:
        response.delete_cookie(
            REFRESH_COOKIE, path=COOKIE_PATH, httponly=True, secure=secure_cookie(), samesite="strict"
        )


@router.get("/me")
def me(user: User = Depends(current_user)) -> Account:
    return account(user)


@admin_router.get("")
def lookup_user(login: Annotated[Login, Query()], db: Session = Depends(get_db)) -> Account:
    user = db.scalar(select(User).where(User.login == login))
    if user is None:
        raise HTTPException(404, "Пользователь не найден")
    return account(user)


@admin_router.patch("/role")
def change_role(
    login: Annotated[Login, Query()], body: RoleChange, db: Session = Depends(get_db)
) -> Account:
    user = db.scalar(select(User).where(User.login == login).with_for_update())
    if user is None:
        raise HTTPException(404, "Пользователь не найден")
    if user.role and user.role.name == "admin":
        raise HTTPException(403, "Роль администратора меняется локальной командой")
    user.role = db.scalars(select(Role).where(Role.name == body.role)).one()
    db.commit()
    return account(user)
