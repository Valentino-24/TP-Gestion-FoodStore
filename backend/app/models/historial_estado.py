"""HistorialEstado model — tracks every state transition for an order."""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, func, Column, Integer, ForeignKey, Text
from sqlmodel import Field, SQLModel


class HistorialEstado(SQLModel, table=True):
    """Audit log for pedido state transitions."""

    __tablename__ = "historial_estado_pedido"

    id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    pedido_id: int = Field(
        sa_column=Column(Integer, ForeignKey("pedido.id"), index=True, nullable=False)
    )
    estado_desde: Optional[str] = Field(
        sa_column=Column(String(50), nullable=True, default=None)
    )
    estado_hasta: str = Field(
        sa_column=Column(String(50), nullable=False)
    )
    usuario_id: Optional[int] = Field(
        sa_column=Column(Integer, ForeignKey("usuario.id"), nullable=True, default=None)
    )
    observacion: Optional[str] = Field(
        sa_column=Column(Text, nullable=True, default=None)
    )
    creado_en: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
