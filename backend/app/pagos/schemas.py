"""Pagos schemas — request/response models for payment processing."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PagoCreate(BaseModel):
    """Request body for initiating a payment."""

    pedido_id: int = Field(..., gt=0, description="Pedido ID to pay for")
    mp_token: Optional[str] = Field(None, description="MercadoPago card token (from frontend)")


class PagoResponse(BaseModel):
    """Response with payment data."""

    id: int
    pedido_id: int
    monto: float
    metodo: str
    estado: str
    mp_pago_id: Optional[str] = None
    mp_status: Optional[str] = None
    creado_en: datetime
    actualizado_en: datetime

    model_config = {"from_attributes": True}


class PagoWebhookPayload(BaseModel):
    """MercadoPago webhook payload (simplified)."""

    action: Optional[str] = None
    data: Optional[dict] = None
    type: Optional[str] = None
