"""Categoria service — business logic for product categories."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status

from app.categorias.repository import CategoriaRepository
from app.categorias.schemas import CategoriaCreate, CategoriaUpdate
from app.models.categoria import Categoria


class CategoriaService:
    """Service layer for category management."""

    def __init__(self, repo: CategoriaRepository):
        """Initialize with repository dependency."""
        self.repo = repo

    async def create(self, data: CategoriaCreate) -> Categoria:
        """Create a new category.

        Args:
            data: Category creation data.

        Returns:
            The created category.

        Raises:
            HTTPException 409: If category name already exists.
        """
        existing = await self.repo.get_by_name(data.nombre)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una categoria con el nombre '{data.nombre}'",
            )

        categoria = Categoria(
            nombre=data.nombre,
            descripcion=data.descripcion,
            activo=True,
        )
        return await self.repo.create(categoria)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Categoria]:
        """Get all active categories ordered by name.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of active categories.
        """
        return await self.repo.get_active(skip=skip, limit=limit)

    async def get_by_id(self, categoria_id: int) -> Categoria:
        """Get a single category by ID.

        Args:
            categoria_id: The category ID.

        Returns:
            The category.

        Raises:
            HTTPException 404: If category not found.
        """
        categoria = await self.repo.get_by_id(categoria_id)
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria no encontrada",
            )
        return categoria

    async def update(self, categoria_id: int, data: CategoriaUpdate) -> Categoria:
        """Update a category.

        Args:
            categoria_id: The category ID to update.
            data: Fields to update.

        Returns:
            The updated category.

        Raises:
            HTTPException 404: If category not found.
            HTTPException 409: If new name conflicts with existing category.
        """
        categoria = await self.get_by_id(categoria_id)

        # Check name uniqueness if changing nombre
        if data.nombre is not None and data.nombre != categoria.nombre:
            existing = await self.repo.get_by_name(data.nombre)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe una categoria con el nombre '{data.nombre}'",
                )

        # Apply updates (only provided fields)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(categoria, field, value)

        categoria.actualizado_en = datetime.now(timezone.utc)
        return await self.repo.update(categoria)

    async def delete(self, categoria_id: int) -> None:
        """Soft-delete a category by setting activo=False.

        Args:
            categoria_id: The category ID to delete.

        Raises:
            HTTPException 404: If category not found.
        """
        categoria = await self.get_by_id(categoria_id)
        categoria.activo = False
        categoria.actualizado_en = datetime.now(timezone.utc)
        await self.repo.update(categoria)
