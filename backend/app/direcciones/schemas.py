"""Direcciones schemas — request/response models with validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DireccionCreate(BaseModel):
    """Request body for creating an address."""

    calle: str = Field(..., min_length=1, max_length=200, description="Street name")
    numero: str = Field(..., min_length=1, max_length=20, description="Street number")
    ciudad: str = Field(..., min_length=1, max_length=100, description="City")
    provincia: str = Field(..., min_length=1, max_length=100, description="Province")
    codigo_postal: str = Field(..., min_length=1, max_length=20, description="Postal code")
    telefono_contacto: Optional[str] = Field(None, max_length=50, description="Contact phone")


class DireccionUpdate(BaseModel):
    """Request body for updating an address."""

    calle: Optional[str] = Field(None, min_length=1, max_length=200)
    numero: Optional[str] = Field(None, min_length=1, max_length=20)
    ciudad: Optional[str] = Field(None, min_length=1, max_length=100)
    provincia: Optional[str] = Field(None, min_length=1, max_length=100)
    codigo_postal: Optional[str] = Field(None, min_length=1, max_length=20)
    telefono_contacto: Optional[str] = Field(None, max_length=50)


class DireccionResponse(BaseModel):
    """Response with address data."""

    id: int
    usuario_id: int
    calle: str
    numero: str
    ciudad: str
    provincia: str
    codigo_postal: str
    telefono_contacto: Optional[str] = None
    activo: bool
    creado_en: datetime
    actualizado_en: datetime

    model_config = {"from_attributes": True}
