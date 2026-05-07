"""Categorias schemas — request/response models with validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CategoriaCreate(BaseModel):
    """Request body for creating a category."""

    nombre: str = Field(..., min_length=1, max_length=100, description="Category name")
    descripcion: Optional[str] = Field(None, max_length=500, description="Optional description")


class CategoriaUpdate(BaseModel):
    """Request body for updating a category.
    
    All fields are optional — only provided fields will be updated.
    """

    nombre: Optional[str] = Field(None, min_length=1, max_length=100, description="Category name")
    descripcion: Optional[str] = Field(None, max_length=500, description="Optional description")
    activo: Optional[bool] = Field(None, description="Whether the category is active")


class CategoriaResponse(BaseModel):
    """Response with category data."""

    id: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool
    creado_en: datetime
    actualizado_en: datetime

    model_config = {"from_attributes": True}
