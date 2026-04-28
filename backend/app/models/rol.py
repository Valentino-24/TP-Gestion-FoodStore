"""Rol model for seed data."""

from sqlalchemy import Integer, String
from sqlmodel import Field

from app.database import Base


class Rol(Base, table=True):
    """Role table for RBAC."""
    
    __tablename__ = "rol"
    
    id: int = Field(primary_key=True)
    nombre: str = Field(unique=True, index=True)
    descripcion: str = Field(default="")