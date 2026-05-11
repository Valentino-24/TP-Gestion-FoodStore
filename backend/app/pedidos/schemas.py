"""Pedidos schemas — request/response models with validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PedidoItemCreate(BaseModel):
    """Request body for a single item within a pedido creation."""

    producto_id: int = Field(..., gt=0, description="Product ID")
    producto_nombre: str = Field(..., min_length=1, max_length=200, description="Product name at time of order")
    cantidad: int = Field(..., ge=1, description="Quantity")
    precio_unitario: float = Field(..., ge=0, description="Unit price at time of order")


class PedidoCreate(BaseModel):
    """Request body for creating a pedido."""

    items: list[PedidoItemCreate] = Field(..., min_length=1, description="Order items")
    direccion_id: int = Field(..., gt=0, description="Shipping address ID")
    forma_pago_id: int = Field(..., gt=0, description="Payment method ID")


class PedidoItemResponse(BaseModel):
    """Response with pedido item data."""

    id: int
    producto_id: int
    producto_nombre: str
    cantidad: int
    precio_unitario: float
    subtotal: float

    model_config = {"from_attributes": True}


class PedidoResponse(BaseModel):
    """Response with pedido data including items."""

    id: int
    usuario_id: int
    estado: str
    total: float
    direccion_id: Optional[int] = None
    forma_pago_id: Optional[int] = None
    creado_en: datetime
    actualizado_en: datetime
    items: list[PedidoItemResponse] = []

    model_config = {"from_attributes": True}


class PedidoEstadoUpdate(BaseModel):
    """Request body for updating pedido estado (admin only)."""

    estado: str = Field(..., min_length=1, description="Target state")


class PedidoListResponse(BaseModel):
    """Paginated response with pedido list."""

    items: list[PedidoResponse]
    total: int
    page: int
    size: int
