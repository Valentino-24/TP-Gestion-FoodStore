"""Pagos router — payment endpoints and webhook receiver."""

from fastapi import APIRouter, Depends, Request, status

from app.database import AsyncSession, get_db
from app.dependencies import CurrentUser
from app.pagos.repository import PagoRepository
from app.pagos.schemas import PagoCreate, PagoResponse, PagoWebhookPayload
from app.pagos.service import PagoService
from app.pedidos.service import PedidoService
from app.pedidos.repository import PedidoRepository

router = APIRouter(prefix="/pagos", tags=["pagos"])


def _get_services(db: AsyncSession) -> tuple[PagoService, PedidoService]:
    """Construct services with their dependencies."""
    pago_repo = PagoRepository(db)
    pedido_repo = PedidoRepository(db)
    return PagoService(pago_repo, db), PedidoService(pedido_repo)


@router.post("/", response_model=PagoResponse, status_code=status.HTTP_201_CREATED)
async def create_pago(
    data: PagoCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Initiate payment for a pedido."""
    pago_service, pedido_service = _get_services(db)
    user_role_names = [rol.nombre for rol in current_user.roles]
    is_admin = "ADMIN" in user_role_names
    pedido = await pedido_service.get_by_id(data.pedido_id, current_user.id, is_admin=is_admin)
    return await pago_service.create_payment(data, pedido)


@router.post("/webhooks/mercadopago", status_code=status.HTTP_200_OK)
async def mercadopago_webhook(
    payload: dict,
    db: AsyncSession = Depends(get_db),
):
    """Receive MercadoPago webhook notifications."""
    pago_repo = PagoRepository(db)
    service = PagoService(pago_repo, db)
    await service.handle_webhook(payload)
    return {"status": "ok"}
