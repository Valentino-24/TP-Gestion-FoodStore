"""Pagos service — business logic for MercadoPago integration."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.pago import Pago
from app.models.pedido import Pedido, can_transition
from app.pagos.repository import PagoRepository
from app.pagos.schemas import PagoCreate


class PagoService:
    """Service layer for payment processing with MercadoPago."""

    def __init__(self, repo: PagoRepository, db: AsyncSession):
        """Initialize with repository and db dependencies."""
        self.repo = repo
        self.db = db

    async def create_payment(self, data: PagoCreate, pedido: Pedido) -> Pago:
        """Initiate a payment for a pedido.

        Uses MercadoPago SDK if credentials are configured,
        otherwise falls back to simulated payment.

        Args:
            data: Payment creation data.
            pedido: The pedido being paid for.

        Returns:
            The created Pago record.
        """
        # Check pedido state
        if pedido.estado != "PENDIENTE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El pedido no está en estado PENDIENTE",
            )

        # Try MercadoPago if configured and token looks valid
        mp_pago_id: Optional[str] = None
        mp_status: Optional[str] = None
        pago_estado = "pendiente"

        if settings.MP_ACCESS_TOKEN and not settings.MP_ACCESS_TOKEN.startswith("TEST-"):
            try:
                import mercadopago
                sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
                payment_data = {
                    "transaction_amount": float(pedido.total),
                    "description": f"Pedido #{pedido.id} - FoodStore",
                    "payment_method_id": "visa",
                    "installments": 1,
                    "token": data.mp_token or "",
                }
                result = sdk.payment().create(payment_data)
                if result.get("status") == 201:
                    response = result.get("response", {})
                    mp_pago_id = str(response.get("id", ""))
                    mp_status = response.get("status", "pending")
                    if mp_status == "approved":
                        pago_estado = "aprobado"
                    elif mp_status == "rejected":
                        pago_estado = "rechazado"
                else:
                    pago_estado = "error"
                    mp_status = "api_error"
            except Exception:
                pago_estado = "error"
                mp_status = "exception"
        else:
            # Simulated payment (dev/test mode)
            mp_pago_id = None
            mp_status = "simulated"
            pago_estado = "aprobado"

        pago = Pago(
            pedido_id=pedido.id,
            monto=pedido.total,
            metodo="mercadopago" if (settings.MP_ACCESS_TOKEN and not settings.MP_ACCESS_TOKEN.startswith("TEST-")) else "simulado",
            estado=pago_estado,
            mp_pago_id=mp_pago_id,
            mp_status=mp_status,
        )
        created = await self.repo.create(pago)

        # If payment approved (or simulated), transition pedido to CONFIRMADO
        if pago_estado == "aprobado" and can_transition(pedido.estado, "CONFIRMADO"):
            pedido.estado = "CONFIRMADO"
            pedido.actualizado_en = datetime.now(timezone.utc)
            await self.repo.update(pedido)

        return created

    async def handle_webhook(self, payload: dict) -> None:
        """Handle MercadoPago webhook notification.

        Args:
            payload: Webhook payload from MercadoPago.
        """
        action = payload.get("action", "")
        data = payload.get("data", {})
        payment_id = data.get("id") if isinstance(data, dict) else None

        if not payment_id:
            return

        if (action == "payment.updated" or "payment" in str(action)) and settings.MP_ACCESS_TOKEN and not settings.MP_ACCESS_TOKEN.startswith("TEST-"):
            try:
                import mercadopago
                sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
                result = sdk.payment().get(int(payment_id))
                if result.get("status") == 200:
                    payment_info = result.get("response", {})
                    status_str = payment_info.get("status", "")
                    # Update payment record
                    pago = await self._find_by_mp_id(str(payment_id))
                    if pago:
                        pago.mp_status = status_str
                        if status_str == "approved":
                            pago.estado = "aprobado"
                        elif status_str in ("rejected", "cancelled", "refunded"):
                            pago.estado = "rechazado"
                        pago.actualizado_en = datetime.now(timezone.utc)
                        await self.repo.update(pago)
            except Exception:
                pass

    async def _find_by_mp_id(self, mp_pago_id: str) -> Optional[Pago]:
        """Find a payment by MercadoPago ID.

        Args:
            mp_pago_id: The MercadoPago payment ID.

        Returns:
            Pago if found, None otherwise.
        """
        result = await self.db.execute(
            self.repo.model.__table__.select().where(
                self.repo.model.mp_pago_id == mp_pago_id  # type: ignore
            )
        )
        return result.scalar_one_or_none()
