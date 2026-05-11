"""Direcciones router — CRUD endpoints for user addresses."""

from fastapi import APIRouter, Depends, status

from app.database import AsyncSession, get_db
from app.dependencies import CurrentUser
from app.direcciones.repository import DireccionRepository
from app.direcciones.schemas import DireccionCreate, DireccionResponse, DireccionUpdate
from app.direcciones.service import DireccionService

router = APIRouter(prefix="/direcciones", tags=["direcciones"])


def _get_service(db: AsyncSession) -> DireccionService:
    """Construct DireccionService with its dependencies."""
    repo = DireccionRepository(db)
    return DireccionService(repo)


@router.get("/", response_model=list[DireccionResponse])
async def list_direcciones(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all active addresses for the authenticated user."""
    service = _get_service(db)
    return await service.get_all(current_user.id)


@router.get("/{direccion_id}", response_model=DireccionResponse)
async def get_direccion(
    direccion_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get a single address by ID. Scoped to the authenticated user."""
    service = _get_service(db)
    return await service.get_by_id(direccion_id, current_user.id)


@router.post("/", response_model=DireccionResponse, status_code=status.HTTP_201_CREATED)
async def create_direccion(
    data: DireccionCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Create a new address for the authenticated user."""
    service = _get_service(db)
    return await service.create(data, current_user.id)


@router.put("/{direccion_id}", response_model=DireccionResponse)
async def update_direccion(
    direccion_id: int,
    data: DireccionUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Update an address. Scoped to the authenticated user."""
    service = _get_service(db)
    return await service.update(direccion_id, data, current_user.id)


@router.delete("/{direccion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_direccion(
    direccion_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete an address. Scoped to the authenticated user."""
    service = _get_service(db)
    await service.delete(direccion_id, current_user.id)
