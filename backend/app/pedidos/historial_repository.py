"""HistorialEstado repository — audit log for state transitions."""

from sqlalchemy import select

from app.models.historial_estado import HistorialEstado


class HistorialRepository:
    """Repository for HistorialEstado CRUD."""

    def __init__(self, db):
        self.db = db

    async def create(self, historial: HistorialEstado) -> HistorialEstado:
        self.db.add(historial)
        await self.db.flush()
        await self.db.refresh(historial)
        return historial

    async def list_by_pedido(self, pedido_id: int) -> list[HistorialEstado]:
        result = await self.db.execute(
            select(HistorialEstado)
            .where(HistorialEstado.pedido_id == pedido_id)
            .order_by(HistorialEstado.creado_en.asc())
        )
        return list(result.scalars().all())
