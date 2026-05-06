"""EstadoPedido model for seed data."""

from sqlmodel import SQLModel, Field
from sqlalchemy import Integer, String, Column


class EstadoPedido(SQLModel, table=True):
    """EstadoPedido table for order state machine."""

    __tablename__ = "estado_pedido"

    id: int = Field(sa_column=Column(Integer, primary_key=True))
    nombre: str = Field(sa_column=Column(String(100), unique=True, index=True, nullable=False))
    descripcion: str = Field(sa_column=Column(String(500), default=""))
