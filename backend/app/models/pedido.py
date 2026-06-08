"""Pedido model with FSM state transitions."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, DateTime, func, Column, Integer, Float, ForeignKey, Text
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.pedido_item import PedidoItem
    from app.models.pago import Pago
    from app.models.historial_estado import HistorialEstado


# Valid state transitions
ESTADO_TRANSITIONS = {
    "PENDIENTE": ["CONFIRMADO", "CANCELADO"],
    "CONFIRMADO": ["EN_PREPARACION", "CANCELADO"],
    "EN_PREPARACION": ["EN_CAMINO"],
    "EN_CAMINO": ["ENTREGADO"],
    "ENTREGADO": [],
    "CANCELADO": [],
}


def can_transition(from_state: str, to_state: str) -> bool:
    """Check if a state transition is valid."""
    allowed = ESTADO_TRANSITIONS.get(from_state, [])
    return to_state in allowed


class Pedido(SQLModel, table=True):
    """Order with FSM-based estado management."""

    __tablename__ = "pedido"

    id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    usuario_id: int = Field(
        sa_column=Column(Integer, ForeignKey("usuario.id"), index=True, nullable=False)
    )
    estado: str = Field(
        sa_column=Column(String(50), ForeignKey("estado_pedido.nombre"), index=True, nullable=False, default="PENDIENTE")
    )
    total: float = Field(sa_column=Column(Float, nullable=False, default=0.0))
    direccion_id: Optional[int] = Field(
        sa_column=Column(Integer, ForeignKey("direccion.id"), nullable=True)
    )
    direccion_snapshot: Optional[str] = Field(
        sa_column=Column(Text, nullable=True, default=None)
    )
    forma_pago_id: Optional[int] = Field(
        sa_column=Column(Integer, ForeignKey("forma_pago.id"), nullable=True)
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
    items: list["PedidoItem"] = Relationship(
        back_populates="pedido",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    pagos: list["Pago"] = Relationship(
        back_populates="pedido",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    historial: list["HistorialEstado"] = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"},
    )
