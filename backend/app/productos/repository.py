"""Producto repository — data access for food products."""

from typing import Optional

from sqlalchemy import select, func

from app.models.producto import Producto
from app.repositories.base import BaseRepository


class ProductoRepository(BaseRepository[Producto]):
    """Repository for Producto CRUD operations."""

    def __init__(self, db):
        """Initialize with Producto model."""
        super().__init__(db, Producto)

    async def get_active(
        self,
        skip: int = 0,
        limit: int = 100,
        categoria_id: Optional[int] = None,
    ) -> list[Producto]:
        """Get active products with optional category filter.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            categoria_id: Optional category ID to filter by.

        Returns:
            List of active products ordered by name.
        """
        query = (
            select(self.model)
            .where(self.model.activo.is_(True))
            .order_by(self.model.nombre)
            .offset(skip)
            .limit(limit)
        )

        if categoria_id is not None:
            query = query.where(self.model.categoria_id == categoria_id)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_active(self, categoria_id: Optional[int] = None) -> int:
        """Count active products with optional category filter.

        Args:
            categoria_id: Optional category ID to filter by.

        Returns:
            Total count of active products.
        """
        query = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.activo.is_(True))
        )

        if categoria_id is not None:
            query = query.where(self.model.categoria_id == categoria_id)

        result = await self.db.execute(query)
        return result.scalar_one()
