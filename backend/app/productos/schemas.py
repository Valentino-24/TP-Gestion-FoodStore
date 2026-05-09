"""Productos schemas — request/response models with validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProductoCreate(BaseModel):
    """Request body for creating a product."""

    nombre: str = Field(..., min_length=1, max_length=200, description="Product name")
    descripcion: Optional[str] = Field(None, max_length=1000, description="Optional description")
    precio: float = Field(..., ge=0, description="Product price (must be >= 0)")
    categoria_id: int = Field(..., gt=0, description="Category ID (FK to categoria)")
    imagen_url: Optional[str] = Field(None, max_length=500, description="Optional image URL")


class ProductoUpdate(BaseModel):
    """Request body for updating a product.

    All fields are optional — only provided fields will be updated.
    """

    nombre: Optional[str] = Field(None, min_length=1, max_length=200, description="Product name")
    descripcion: Optional[str] = Field(None, max_length=1000, description="Optional description")
    precio: Optional[float] = Field(None, ge=0, description="Product price (must be >= 0)")
    categoria_id: Optional[int] = Field(None, gt=0, description="Category ID (FK to categoria)")
    imagen_url: Optional[str] = Field(None, max_length=500, description="Optional image URL")
    activo: Optional[bool] = Field(None, description="Whether the product is active")


class ProductoResponse(BaseModel):
    """Response with product data."""

    id: int
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    categoria_id: int
    imagen_url: Optional[str] = None
    activo: bool
    creado_en: datetime
    actualizado_en: datetime

    model_config = {"from_attributes": True}


class ProductoListResponse(BaseModel):
    """Paginated response with product list."""

    items: list[ProductoResponse]
    total: int
    page: int
    size: int
