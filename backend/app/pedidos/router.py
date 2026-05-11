"""Pedidos router — CRUD endpoints with FSM state management."""

from fastapi import APIRouter, Depends, Query, status

from app.database import AsyncSession, get_db
from app.dependencies import CurrentUser, require_role
from app.pedidos.repository import PedidoRepository
from app.pedidos.schemas import PedidoCreate, PedidoEstadoUpdate, PedidoListResponse, PedidoResponse
from app.pedidos.service import PedidoService

router = APIRouter(prefix="/pedidos", tags=["pedidos"])


def _get_service(db: AsyncSession) -> PedidoService:
    """Construct PedidoService with its dependencies."""
    repo = PedidoRepository(db)
    return PedidoService(repo)


@router.post("/", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
async def create_pedido(
    data: PedidoCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Create a new pedido. Requires authentication."""
    service = _get_service(db)
    return await service.create(data, current_user.id)


@router.get("/", response_model=PedidoListResponse)
async def list_pedidos(
    current_user: CurrentUser,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
):
    """List pedidos. Regular users see their own. ADMIN sees all."""
    service = _get_service(db)
    user_role_names = [rol.nombre for rol in current_user.roles]
    is_admin = "ADMIN" in user_role_names

    if is_admin:
        return await service.get_all_pedidos(page=page, size=size)
    else:
        return await service.get_user_pedidos(current_user.id, page=page, size=size)


@router.get("/{pedido_id}", response_model=PedidoResponse)
async def get_pedido(
    pedido_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get a pedido by ID. Users see only their own. ADMIN sees all."""
    service = _get_service(db)
    user_role_names = [rol.nombre for rol in current_user.roles]
    is_admin = "ADMIN" in user_role_names
    return await service.get_by_id(pedido_id, current_user.id, is_admin=is_admin)


@router.patch("/{pedido_id}/estado", response_model=PedidoResponse)
async def update_pedido_estado(
    pedido_id: int,
    data: PedidoEstadoUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_role(["ADMIN"])),
):
    """Update pedido estado (FSM). Requires ADMIN role."""
    service = _get_service(db)
    return await service.update_estado(pedido_id, data)
