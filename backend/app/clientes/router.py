"""Clientes router — CRUD endpoints for customer management."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.database import AsyncSession, get_db
from app.dependencies import CurrentUser, require_role
from app.clientes.repository import ClienteRepository
from app.clientes.schemas import (
    ClienteCreate,
    ClienteListResponse,
    ClienteResponse,
    ClienteUpdate,
)
from app.clientes.service import ClienteService

router = APIRouter(prefix="/clientes", tags=["clientes"])


def _get_service(db: AsyncSession) -> ClienteService:
    """Construct ClienteService with its dependencies."""
    repo = ClienteRepository(db)
    return ClienteService(repo, db)


@router.get("/me", response_model=ClienteResponse)
async def get_my_cliente(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get the customer profile linked to the authenticated user (by email). Requires authentication."""
    service = _get_service(db)
    cliente = await service.get_by_email(current_user.email)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontro un cliente vinculado a este usuario",
        )
    return cliente


@router.put("/me", response_model=ClienteResponse)
async def update_my_cliente(
    data: ClienteUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Update the authenticated user's own customer profile (matched by email). Requires authentication."""
    service = _get_service(db)
    cliente = await service.get_by_email(current_user.email)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontro un cliente vinculado a este usuario",
        )
    return await service.update(cliente.id, data)


@router.get("/", response_model=ClienteListResponse)
async def list_clientes(
    current_user: CurrentUser,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
):
    """List active customers with pagination. Requires authentication."""
    service = _get_service(db)
    return await service.get_all(page=page, size=size)


@router.get("/{cliente_id}", response_model=ClienteResponse)
async def get_cliente(
    cliente_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get a single customer by ID.

    ADMIN can access any customer.
    CLIENT can only access their own customer (matched by email).
    """
    service = _get_service(db)
    cliente = await service.get_by_id(cliente_id)

    # CLIENT role can only access their own record (email-based binding)
    user_role_names = [role.nombre for role in current_user.roles]
    if "CLIENT" in user_role_names and cliente.email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a este cliente",
        )

    return cliente


@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
async def create_cliente(
    data: ClienteCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_role(["ADMIN"])),
):
    """Create a new customer. Requires ADMIN role."""
    service = _get_service(db)
    return await service.create(data)


@router.put("/{cliente_id}", response_model=ClienteResponse)
async def update_cliente(
    cliente_id: int,
    data: ClienteUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_role(["ADMIN"])),
):
    """Update a customer. Requires ADMIN role."""
    service = _get_service(db)
    return await service.update(cliente_id, data)


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cliente(
    cliente_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_role(["ADMIN"])),
):
    """Soft-delete a customer. Requires ADMIN role."""
    service = _get_service(db)
    await service.delete(cliente_id)
