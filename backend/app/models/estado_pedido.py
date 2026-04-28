"""EstadoPedido model for seed data."""

from sqlalchemy import Integer, String
from sqlmodel import Field

from app.database import Base


class EstadoPedido(Base, table=True):
    """EstadoPedido table for order state machine."""
    
    __tablename__ = "estado_pedido"
    
    id: int = Field(primary_key=True)
    nombre: str = Field(unique=True, index=True)
    descripcion: str = Field(default="")