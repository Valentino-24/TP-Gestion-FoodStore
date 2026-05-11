"""PedidoItem model — individual items within an order."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, DateTime, func, Column, Integer, Float, ForeignKey, Text
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.pedido import Pedido


class PedidoItem(SQLModel, table=True):
    """Individual product line within a pedido."""

    __tablename__ = "pedido_item"

    id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    pedido_id: int = Field(
        sa_column=Column(Integer, ForeignKey("pedido.id"), index=True, nullable=False)
    )
    producto_id: int = Field(
        sa_column=Column(Integer, ForeignKey("producto.id"), nullable=False)
    )
    producto_nombre: str = Field(
        sa_column=Column(String(200), nullable=False)
    )
    cantidad: int = Field(sa_column=Column(Integer, nullable=False, default=1))
    precio_unitario: float = Field(sa_column=Column(Float, nullable=False))
    subtotal: float = Field(sa_column=Column(Float, nullable=False))

    # Relationships
    pedido: "Pedido" = Relationship(back_populates="items")
