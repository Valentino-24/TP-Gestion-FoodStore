"""Categoria repository — data access for product categories."""

from typing import Optional

from sqlalchemy import select, func

from app.models.categoria import Categoria
from app.repositories.base import BaseRepository


class CategoriaRepository(BaseRepository[Categoria]):
    """Repository for Categoria CRUD operations."""

    def __init__(self, db):
        """Initialize with Categoria model."""
        super().__init__(db, Categoria)

    async def get_by_name(self, nombre: str) -> Optional[Categoria]:
        """Find a category by its unique name.

        Args:
            nombre: The category name to search for.

        Returns:
            The category if found, None otherwise.
        """
        result = await self.db.execute(
            select(self.model).where(func.lower(self.model.nombre) == func.lower(nombre))
        )
        return result.scalar_one_or_none()

    async def get_active(self, skip: int = 0, limit: int = 100) -> list[Categoria]:
        """Get all active categories ordered by name.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of active categories.
        """
        result = await self.db.execute(
            select(self.model)
            .where(self.model.activo.is_(True))
            .order_by(self.model.nombre)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_active(self) -> int:
        """Count active categories.

        Returns:
            Total count of active categories.
        """
        result = await self.db.execute(
            select(func.count()).select_from(self.model).where(self.model.activo.is_(True))
        )
        return result.scalar_one()
