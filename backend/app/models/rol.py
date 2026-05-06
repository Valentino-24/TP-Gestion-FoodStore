"""Rol model for seed data."""

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Column
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class Rol(SQLModel, table=True):
    """Role table for RBAC."""

    __tablename__ = "rol"

    id: int = Field(sa_column=Column(Integer, primary_key=True))
    nombre: str = Field(sa_column=Column(String(100), unique=True, index=True, nullable=False))
    descripcion: str = Field(sa_column=Column(String(500), default=""))

    # Relationships
    usuarios: list["Usuario"] = Relationship(
        back_populates="roles",
        sa_relationship_kwargs={
            "secondary": "usuario_rol",
            "lazy": "selectin",
        },
    )
