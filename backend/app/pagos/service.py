"""Pagos service — business logic for MercadoPago integration (real payments)."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.pago import Pago
from app.models.historial_estado import HistorialEstado
from app.models.pedido import Pedido, can_transition
from app.pagos.repository import PagoRepository
from app.pagos.schemas import PagoCreate
from app.cocina.event_manager import EventManager, KitchenEvent, event_manager as default_event_manager


class PagoService:
    """Service layer for payment processing with MercadoPago."""

    def __init__(
        self,
        repo: PagoRepository,
        db: AsyncSession,
        event_manager: Optional[EventManager] = None,
    ):
        """Initialize with repository and db dependencies."""
        self.repo = repo
        self.db = db
        self.event_manager = event_manager

    async def create_payment(self, data: PagoCreate, pedido: Pedido) -> Pago:
        """Initiate a payment for a pedido using MercadoPago SDK.

        Args:
            data: Payment creation data with mp_token from Card Brick.
            pedido: The pedido being paid for.

        Returns:
            The created Pago record.

        Raises:
            HTTPException 400: If pedido not in PENDIENTE state or uses Efectivo.
            HTTPException 503: If MP_ACCESS_TOKEN is not configured.
        """
        # Check pedido state
        if pedido.estado != "PENDIENTE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El pedido no está en estado PENDIENTE",
            )

        # Efectivo doesn't require online payment
        if pedido.forma_pago_id == 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El pedido usa Efectivo, no requiere pago online",
            )

        # Require MP credentials
        if not settings.MP_ACCESS_TOKEN:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MercadoPago no configurado",
            )

        mp_pago_id: Optional[str] = None
        mp_status: Optional[str] = None
        pago_estado = "pendiente"

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

        pago = Pago(
            pedido_id=pedido.id,
            monto=pedido.total,
            metodo="mercadopago",
            estado=pago_estado,
            mp_pago_id=mp_pago_id,
            mp_status=mp_status,
        )
        created = await self.repo.create(pago)

        # If payment approved, transition pedido to CONFIRMADO
        if pago_estado == "aprobado" and can_transition(pedido.estado, "CONFIRMADO"):
            from_state = pedido.estado
            pedido.estado = "CONFIRMADO"
            pedido.actualizado_en = datetime.now(timezone.utc)
            await self.repo.update(pedido)

            # Record historial for the auto-transition
            historial = HistorialEstado(
                pedido_id=pedido.id,
                estado_desde=from_state,
                estado_hasta="CONFIRMADO",
                observacion="Pago aprobado",
            )
            self.db.add(historial)
            await self.db.flush()

            # Emit kitchen event if event_manager is available
            if self.event_manager:
                event = KitchenEvent(
                    type="PEDIDO_CONFIRMADO",
                    pedido_id=pedido.id,
                    data={
                        "pedido_id": pedido.id,
                        "estado": "CONFIRMADO",
                        "from_state": from_state,
                    },
                )
                await self.event_manager.broadcast(EventManager.CHANNEL_KITCHEN, event)

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

        if (action == "payment.updated" or "payment" in str(action)) and settings.MP_ACCESS_TOKEN:
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
