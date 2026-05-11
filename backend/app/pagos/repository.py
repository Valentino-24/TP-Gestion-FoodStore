"""Pagos repository — data access for payments."""

from app.models.pago import Pago
from app.repositories.base import BaseRepository


class PagoRepository(BaseRepository[Pago]):
    """Repository for Pago CRUD operations."""

    def __init__(self, db):
        """Initialize with Pago model."""
        super().__init__(db, Pago)

    async def get_by_pedido_id(self, pedido_id: int) -> list[Pago]:
        """Get all payments for a pedido.

        Args:
            pedido_id: The pedido ID.

        Returns:
            List of payments.
        """
        result = await self.db.execute(
            self.model.__table__.select().where(
                self.model.pedido_id == pedido_id  # type: ignore
            ).order_by(self.model.creado_en.desc())
        )
        return list(result.scalars().all())
