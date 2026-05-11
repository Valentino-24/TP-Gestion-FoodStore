"""Direccion model for user shipping addresses."""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, func, Column, Integer, Boolean, ForeignKey
from sqlmodel import SQLModel, Field


class Direccion(SQLModel, table=True):
    """User shipping address with soft delete support."""

    __tablename__ = "direccion"

    id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    usuario_id: int = Field(
        sa_column=Column(Integer, ForeignKey("usuario.id"), index=True, nullable=False)
    )
    calle: str = Field(sa_column=Column(String(200), nullable=False))
    numero: str = Field(sa_column=Column(String(20), nullable=False))
    ciudad: str = Field(sa_column=Column(String(100), nullable=False))
    provincia: str = Field(sa_column=Column(String(100), nullable=False))
    codigo_postal: str = Field(sa_column=Column(String(20), nullable=False))
    telefono_contacto: Optional[str] = Field(
        sa_column=Column(String(50), default=None, nullable=True)
    )
    activo: bool = Field(sa_column=Column(Boolean, default=True, nullable=False))
    creado_en: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    actualizado_en: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )
    )
