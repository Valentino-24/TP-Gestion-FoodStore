"""Pedidos repository — data access for orders."""

from typing import Optional

from sqlalchemy import select, func

from app.models.pedido import Pedido
from app.models.pedido_item import PedidoItem
from app.repositories.base import BaseRepository


class PedidoRepository(BaseRepository[Pedido]):
    """Repository for Pedido CRUD operations."""

    def __init__(self, db):
        """Initialize with Pedido model."""
        super().__init__(db, Pedido)

    async def get_user_pedidos(
        self, usuario_id: int, skip: int = 0, limit: int = 20
    ) -> list[Pedido]:
        """Get all pedidos for a user with pagination, newest first.

        Args:
            usuario_id: The user ID.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of pedidos with items loaded.
        """
        result = await self.db.execute(
            select(Pedido)
            .where(Pedido.usuario_id == usuario_id)
            .order_by(Pedido.creado_en.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_all_pedidos(
        self, skip: int = 0, limit: int = 20
    ) -> list[Pedido]:
        """Get all pedidos with pagination (admin), newest first.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of pedidos.
        """
        result = await self.db.execute(
            select(Pedido)
            .order_by(Pedido.creado_en.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_user_pedidos(self, usuario_id: int) -> int:
        """Count pedidos for a user.

        Args:
            usuario_id: The user ID.

        Returns:
            Total count.
        """
        result = await self.db.execute(
            select(func.count())
            .select_from(Pedido)
            .where(Pedido.usuario_id == usuario_id)
        )
        return result.scalar_one()

    async def count_all_pedidos(self) -> int:
        """Count all pedidos.

        Returns:
            Total count.
        """
        result = await self.db.execute(
            select(func.count()).select_from(Pedido)
        )
        return result.scalar_one()

    async def get_pedido_with_items(self, pedido_id: int) -> Optional[Pedido]:
        """Get pedido by ID with items eagerly loaded.

        Args:
            pedido_id: The pedido ID.

        Returns:
            Pedido with items if found, None otherwise.
        """
        result = await self.db.execute(
            select(Pedido)
            .where(Pedido.id == pedido_id)
        )
        return result.scalar_one_or_none()

    async def create_pedido_item(self, item: PedidoItem) -> PedidoItem:
        """Create a pedido item.

        Args:
            item: The PedidoItem to create.

        Returns:
            The created item.
        """
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def get_by_id_raw(self, pedido_id: int) -> Optional[Pedido]:
        """Get pedido by ID without relationship loading (for state checks).

        Args:
            pedido_id: The pedido ID.

        Returns:
            Pedido if found, None otherwise.
        """
        return await self.get_by_id(pedido_id)
