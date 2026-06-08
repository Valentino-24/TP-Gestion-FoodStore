"""Producto model for food products."""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, func, Column, Integer, Boolean, Text, Float, BigInteger, ForeignKey
from sqlmodel import SQLModel, Field


class Producto(SQLModel, table=True):
    """Food product with category association and soft delete support."""

    __tablename__ = "producto"

    id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    nombre: str = Field(
        sa_column=Column(String(200), index=True, nullable=False)
    )
    descripcion: Optional[str] = Field(sa_column=Column(Text, default=None, nullable=True))
    precio: float = Field(sa_column=Column(Float, nullable=False))
    categoria_id: int = Field(
        sa_column=Column(Integer, ForeignKey("categoria.id"), index=True, nullable=False)
    )
    imagen_url: Optional[str] = Field(
        sa_column=Column(String(500), default=None, nullable=True)
    )
    activo: bool = Field(sa_column=Column(Boolean, default=True, nullable=False))
    stock_cantidad: Optional[int] = Field(
        sa_column=Column(Integer, default=0, nullable=True)
    )
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
