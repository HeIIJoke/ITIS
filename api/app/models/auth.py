from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.app.core.database import Base


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int | None] = mapped_column(ForeignKey("public.roles.id"))
    login: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool | None] = mapped_column(Boolean)
    role: Mapped[Role | None] = relationship()


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("public.users.id", ondelete="CASCADE"))
    refresh_token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
