"""Direcciones repository — data access for user addresses."""

from typing import Optional

from sqlalchemy import select, func

from app.models.direccion import Direccion
from app.repositories.base import BaseRepository


class DireccionRepository(BaseRepository[Direccion]):
    """Repository for Direccion CRUD operations."""

    def __init__(self, db):
        """Initialize with Direccion model."""
        super().__init__(db, Direccion)

    async def get_user_addresses(self, usuario_id: int) -> list[Direccion]:
        """Get all active addresses for a user.

        Args:
            usuario_id: The user ID.

        Returns:
            List of active addresses.
        """
        result = await self.db.execute(
            select(Direccion)
            .where(Direccion.usuario_id == usuario_id, Direccion.activo.is_(True))
            .order_by(Direccion.creado_en.desc())
        )
        return list(result.scalars().all())

    async def get_user_address_by_id(self, address_id: int, usuario_id: int) -> Optional[Direccion]:
        """Get a specific address by ID, scoped to user.

        Args:
            address_id: The address ID.
            usuario_id: The user ID to scope to.

        Returns:
            The address if found and owned by user, None otherwise.
        """
        result = await self.db.execute(
            select(Direccion).where(
                Direccion.id == address_id,
                Direccion.usuario_id == usuario_id,
            )
        )
        return result.scalar_one_or_none()

    async def count_user_addresses(self, usuario_id: int) -> int:
        """Count active addresses for a user.

        Args:
            usuario_id: The user ID.

        Returns:
            Total count of active addresses.
        """
        result = await self.db.execute(
            select(func.count())
            .select_from(Direccion)
            .where(Direccion.usuario_id == usuario_id, Direccion.activo.is_(True))
        )
        return result.scalar_one()
