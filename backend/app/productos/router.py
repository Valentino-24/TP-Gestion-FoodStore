"""Productos router — CRUD endpoints for food products."""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.database import AsyncSession, get_db
from app.dependencies import CurrentUser, require_role
from app.productos.repository import ProductoRepository
from app.productos.schemas import (
    ProductoCreate,
    ProductoListResponse,
    ProductoResponse,
    ProductoUpdate,
)
from app.productos.service import ProductoService

router = APIRouter(prefix="/productos", tags=["productos"])


def _get_service(db: AsyncSession) -> ProductoService:
    """Construct ProductoService with its dependencies."""
    repo = ProductoRepository(db)
    return ProductoService(repo, db)


@router.get("/", response_model=ProductoListResponse)
async def list_productos(
    current_user: CurrentUser,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    categoria_id: Optional[int] = Query(None, gt=0, description="Filter by category ID"),
    db: AsyncSession = Depends(get_db),
):
    """List active products with pagination and optional category filter. Requires authentication."""
    service = _get_service(db)
    return await service.get_all(page=page, size=size, categoria_id=categoria_id)


@router.get("/{producto_id}", response_model=ProductoResponse)
async def get_producto(
    producto_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get a single product by ID. Requires authentication."""
    service = _get_service(db)
    return await service.get_by_id(producto_id)


@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
async def create_producto(
    data: ProductoCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_role(["ADMIN"])),
):
    """Create a new product. Requires ADMIN role."""
    service = _get_service(db)
    return await service.create(data)


@router.put("/{producto_id}", response_model=ProductoResponse)
async def update_producto(
    producto_id: int,
    data: ProductoUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_role(["ADMIN"])),
):
    """Update a product. Requires ADMIN role."""
    service = _get_service(db)
    return await service.update(producto_id, data)


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_producto(
    producto_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_role(["ADMIN"])),
):
    """Soft-delete a product. Requires ADMIN role."""
    service = _get_service(db)
    await service.delete(producto_id)
