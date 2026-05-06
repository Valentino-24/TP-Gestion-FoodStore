"""RefreshToken model for secure token management."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, DateTime, ForeignKey, func, Column, Integer
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class RefreshToken(SQLModel, table=True):
    """Refresh token table with SHA-256 hash and family tracking for replay detection."""

    __tablename__ = "refresh_token"

    id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
    )
    token_hash: str = Field(sa_column=Column(String(64), unique=True, index=True, nullable=False))
    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    revoked_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), default=None, nullable=True)
    )
    family_id: str = Field(sa_column=Column(String(36), index=True, nullable=False))
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )

    # Relationships
    usuario: "Usuario" = Relationship(back_populates="refresh_tokens", sa_relationship_kwargs={"lazy": "selectin"})
