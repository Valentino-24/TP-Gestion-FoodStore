"""Pago model for payment transactions."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, DateTime, func, Column, Integer, Float, ForeignKey, Text
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.pedido import Pedido


class Pago(SQLModel, table=True):
    """Payment record linked to a pedido."""

    __tablename__ = "pago"

    id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    pedido_id: int = Field(
        sa_column=Column(Integer, ForeignKey("pedido.id"), index=True, nullable=False)
    )
    monto: float = Field(sa_column=Column(Float, nullable=False))
    metodo: str = Field(
        sa_column=Column(String(50), nullable=False, default="mercadopago")
    )
    estado: str = Field(
        sa_column=Column(String(50), nullable=False, default="pendiente")
    )
    mp_pago_id: Optional[str] = Field(
        sa_column=Column(String(100), default=None, nullable=True)
    )
    mp_status: Optional[str] = Field(
        sa_column=Column(String(50), default=None, nullable=True)
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

    # Relationships
    pedido: "Pedido" = Relationship(back_populates="pagos")
