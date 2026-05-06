"""Usuario model for user accounts."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, DateTime, func, Column, Integer
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.rol import Rol
    from app.models.refresh_token import RefreshToken


class Usuario(SQLModel, table=True):
    """User account table with soft delete and audit fields."""

    __tablename__ = "usuario"

    id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    nombre: str = Field(sa_column=Column(String(100), nullable=False))
    apellido: str = Field(sa_column=Column(String(100), nullable=False))
    email: str = Field(sa_column=Column(String(255), unique=True, index=True, nullable=False))
    password_hash: str = Field(sa_column=Column(String(255), nullable=False))
    eliminado_en: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), default=None, nullable=True)
    )
    creado_en: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    actualizado_en: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    )

    # Relationships
    roles: list["Rol"] = Relationship(
        back_populates="usuarios",
        sa_relationship_kwargs={
            "secondary": "usuario_rol",
            "lazy": "selectin",
        },
    )
    refresh_tokens: list["RefreshToken"] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
