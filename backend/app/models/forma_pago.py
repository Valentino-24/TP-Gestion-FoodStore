"""FormaPago model for seed data."""

from sqlalchemy import Integer, String, Boolean
from sqlmodel import Field

from app.database import Base


class FormaPago(Base, table=True):
    """FormaPago table for payment methods."""
    
    __tablename__ = "forma_pago"
    
    id: int = Field(primary_key=True)
    nombre: str = Field(unique=True, index=True)
    activo: bool = Field(default=True)