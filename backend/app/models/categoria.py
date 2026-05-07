"""Categoria model for product categories."""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, func, Column, Integer, Boolean, Text
from sqlmodel import SQLModel, Field


class Categoria(SQLModel, table=True):
    """Product category with soft delete support."""

    __tablename__ = "categoria"

    id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    nombre: str = Field(
        sa_column=Column(String(100), unique=True, index=True, nullable=False)
    )
    descripcion: Optional[str] = Field(sa_column=Column(Text, default=None, nullable=True))
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
