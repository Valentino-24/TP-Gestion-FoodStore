"""Clientes schemas — request/response models with validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ClienteCreate(BaseModel):
    """Request body for creating a customer."""

    nombre: str = Field(..., min_length=1, max_length=100, description="Customer first name")
    apellido: str = Field(..., min_length=1, max_length=100, description="Customer last name")
    email: str = Field(..., max_length=255, description="Customer email (must be unique)")
    telefono: Optional[str] = Field(None, max_length=50, description="Phone number")
    direccion: Optional[str] = Field(None, max_length=1000, description="Street address")


class ClienteUpdate(BaseModel):
    """Request body for updating a customer.

    All fields are optional — only provided fields will be updated.
    """

    nombre: Optional[str] = Field(None, min_length=1, max_length=100, description="Customer first name")
    apellido: Optional[str] = Field(None, min_length=1, max_length=100, description="Customer last name")
    email: Optional[str] = Field(None, max_length=255, description="Customer email (must be unique)")
    telefono: Optional[str] = Field(None, max_length=50, description="Phone number")
    direccion: Optional[str] = Field(None, max_length=1000, description="Street address")
    activo: Optional[bool] = Field(None, description="Whether the customer is active")


class ClienteResponse(BaseModel):
    """Response with customer data."""

    id: int
    nombre: str
    apellido: str
    email: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    activo: bool
    creado_en: datetime
    actualizado_en: datetime

    model_config = {"from_attributes": True}


class ClienteListResponse(BaseModel):
    """Paginated response with customer list."""

    items: list[ClienteResponse]
    total: int
    page: int
    size: int
