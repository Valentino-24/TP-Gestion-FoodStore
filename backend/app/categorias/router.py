"""Categorias router — CRUD endpoints for product categories."""

from fastapi import APIRouter, Depends, status

from app.categorias.repository import CategoriaRepository
from app.categorias.schemas import CategoriaCreate, CategoriaResponse, CategoriaUpdate
from app.categorias.service import CategoriaService
from app.database import AsyncSession, get_db
from app.dependencies import CurrentUser, require_role

router = APIRouter(prefix="/categorias", tags=["categorias"])


def _get_service(db: AsyncSession) -> CategoriaService:
    """Construct CategoriaService with its dependencies."""
    repo = CategoriaRepository(db)
    return CategoriaService(repo)


@router.get("/", response_model=list[CategoriaResponse])
async def list_categorias(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all active categories. Requires authentication."""
    service = _get_service(db)
    return await service.get_all()


@router.get("/{categoria_id}", response_model=CategoriaResponse)
async def get_categoria(
    categoria_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get a single category by ID. Requires authentication."""
    service = _get_service(db)
    return await service.get_by_id(categoria_id)


@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
async def create_categoria(
    data: CategoriaCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_role(["ADMIN"])),
):
    """Create a new category. Requires ADMIN role."""
    service = _get_service(db)
    return await service.create(data)


@router.put("/{categoria_id}", response_model=CategoriaResponse)
async def update_categoria(
    categoria_id: int,
    data: CategoriaUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_role(["ADMIN"])),
):
    """Update a category. Requires ADMIN role."""
    service = _get_service(db)
    return await service.update(categoria_id, data)


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_categoria(
    categoria_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_role(["ADMIN"])),
):
    """Soft-delete a category. Requires ADMIN role."""
    service = _get_service(db)
    await service.delete(categoria_id)
