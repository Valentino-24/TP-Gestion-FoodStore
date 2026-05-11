"""Cliente repository — data access for customers."""

from typing import Optional

from sqlalchemy import select, func

from app.models.cliente import Cliente
from app.repositories.base import BaseRepository


class ClienteRepository(BaseRepository[Cliente]):
    """Repository for Cliente CRUD operations."""

    def __init__(self, db):
        """Initialize with Cliente model."""
        super().__init__(db, Cliente)

    async def get_active(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Cliente]:
        """Get active customers with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of active customers ordered by name.
        """
        query = (
            select(self.model)
            .where(self.model.activo.is_(True))
            .order_by(self.model.apellido, self.model.nombre)
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_active(self) -> int:
        """Count active customers.

        Returns:
            Total count of active customers.
        """
        query = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.activo.is_(True))
        )

        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_by_email(self, email: str) -> Optional[Cliente]:
        """Get a customer by email.

        Args:
            email: The email to look up.

        Returns:
            The customer if found, None otherwise.
        """
        query = select(self.model).where(self.model.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
