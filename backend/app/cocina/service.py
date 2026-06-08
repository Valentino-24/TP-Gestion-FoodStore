"""Cocina service — business logic for the Kitchen Display System."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.pedido import Pedido
from app.cocina.schemas import PedidoCocinaResponse, ItemPedidoCocina


class CocinaService:
    """Service layer for KDS operations."""

    # States visible in the KDS
    KITCHEN_STATES = ("CONFIRMADO", "EN_PREPARACION")

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_pedidos_cocina(self) -> list[PedidoCocinaResponse]:
        """Return all pedidos in kitchen states, ordered by kitchen entry time.

        Filters Pedido where estado IN ('CONFIRMADO', 'EN_PREPARACION'),
        orders by the time they entered the kitchen queue (oldest first),
        and includes items and kitchen entry timestamp.
        """
        result = await self.db.execute(
            select(Pedido)
            .options(
                selectinload(Pedido.items),
                selectinload(Pedido.historial),
            )
            .where(Pedido.estado.in_(self.KITCHEN_STATES))
            .order_by(Pedido.creado_en.asc())
        )
        pedidos = list(result.scalars().all())

        responses = []
        for pedido in pedidos:
            # Find kitchen entry timestamp: first historial entry with estado_hasta = CONFIRMADO
            kitchen_entry = None
            for h in pedido.historial:
                if h.estado_hasta == "CONFIRMADO":
                    kitchen_entry = h.creado_en
                    break

            items = [
                ItemPedidoCocina(
                    producto_nombre=item.producto_nombre,
                    cantidad=item.cantidad,
                    subtotal=item.subtotal,
                )
                for item in (pedido.items or [])
            ]

            responses.append(PedidoCocinaResponse(
                id=pedido.id,
                estado=pedido.estado,
                items=items,
                notas=None,  # Pedido model doesn't have notas field currently
                kitchen_entry_at=kitchen_entry,
                creado_en=pedido.creado_en,
            ))

        return responses
