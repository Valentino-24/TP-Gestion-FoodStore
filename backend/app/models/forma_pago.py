"""FormaPago model for seed data."""

from sqlmodel import SQLModel, Field
from sqlalchemy import Integer, String, Boolean, Column


class FormaPago(SQLModel, table=True):
    """FormaPago table for payment methods."""

    __tablename__ = "forma_pago"

    id: int = Field(sa_column=Column(Integer, primary_key=True))
    nombre: str = Field(sa_column=Column(String(100), unique=True, index=True, nullable=False))
    activo: bool = Field(sa_column=Column(Boolean, default=True))
