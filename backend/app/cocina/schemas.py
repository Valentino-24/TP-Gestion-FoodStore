"""Cocina schemas — request/response models for the KDS module."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ItemPedidoCocina(BaseModel):
    """A pedido item as shown in the KDS."""

    producto_nombre: str
    cantidad: int
    subtotal: float
    personalizacion: Optional[str] = None

    model_config = {"from_attributes": True}


class PedidoCocinaResponse(BaseModel):
    """A pedido as shown in the KDS card."""

    id: int
    estado: str
    items: list[ItemPedidoCocina] = []
    notas: Optional[str] = Field(default=None, alias="notas")
    kitchen_entry_at: Optional[datetime] = None
    creado_en: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}
