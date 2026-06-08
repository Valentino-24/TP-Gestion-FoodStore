"""Pedidos service — business logic with FSM state management."""

import json
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.historial_estado import HistorialEstado
from app.models.pedido import Pedido, can_transition
from app.models.pedido_item import PedidoItem
from app.models.producto import Producto
from app.models.direccion import Direccion
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.pedidos.repository import PedidoRepository
from app.pedidos.historial_repository import HistorialRepository
from app.pedidos.schemas import PedidoCreate, PedidoEstadoUpdate
from app.cocina.event_manager import EventManager, KitchenEvent, event_manager as default_event_manager

# Role-based transition permissions.
# Key: role name, Value: set of (from_state, to_state) tuples allowed.
# Only explicitly listed transitions are allowed per role.
ROLE_TRANSITIONS: dict[str, set[tuple[str, str]]] = {
    "COCINA": {
        ("CONFIRMADO", "EN_PREPARACION"),
        ("EN_PREPARACION", "EN_CAMINO"),
    },
    "PEDIDOS": {
        ("CONFIRMADO", "EN_PREPARACION"),
        ("EN_PREPARACION", "EN_CAMINO"),
        ("EN_CAMINO", "ENTREGADO"),
    },
    "ADMIN": {
        ("PENDIENTE", "CONFIRMADO"),
        ("PENDIENTE", "CANCELADO"),
        ("CONFIRMADO", "EN_PREPARACION"),
        ("CONFIRMADO", "CANCELADO"),
        ("EN_PREPARACION", "EN_CAMINO"),
        ("EN_PREPARACION", "CANCELADO"),
        ("EN_CAMINO", "ENTREGADO"),
    },
}


class PedidoService:
    """Service layer for order management with FSM."""

    def __init__(
        self,
        repo: PedidoRepository,
        db: AsyncSession,
        event_manager: Optional[EventManager] = None,
    ):
        self.repo = repo
        self.db = db
        self.historial_repo = HistorialRepository(db)
        self.event_manager = event_manager

    @staticmethod
    def _get_role_names(usuario: Usuario) -> set[str]:
        """Extract role names from user object."""
        return {rol.nombre for rol in usuario.roles}

    @staticmethod
    def _validate_role_transition(role_names: set[str], from_state: str, to_state: str) -> None:
        """Check if any of the user's roles allow the requested transition.

        Raises HTTPException 403 if no role permits the transition.
        """
        for role in role_names:
            allowed = ROLE_TRANSITIONS.get(role, set())
            if (from_state, to_state) in allowed:
                return  # At least one role allows it
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"El rol no tiene permiso para la transición '{from_state}' → '{to_state}'",
        )

    async def _create_historial(
        self,
        pedido_id: int,
        estado_hasta: str,
        usuario_id: int | None = None,
        estado_desde: str | None = None,
        observacion: str | None = None,
    ) -> HistorialEstado:
        historial = HistorialEstado(
            pedido_id=pedido_id,
            estado_desde=estado_desde,
            estado_hasta=estado_hasta,
            usuario_id=usuario_id,
            observacion=observacion,
        )
        return await self.historial_repo.create(historial)

    async def _capture_direccion_snapshot(self, direccion_id: int) -> str | None:
        result = await self.db.execute(
            select(Direccion).where(Direccion.id == direccion_id)
        )
        direccion = result.scalar_one_or_none()
        if not direccion:
            return None
        return json.dumps({
            "calle": direccion.calle,
            "numero": direccion.numero,
            "ciudad": direccion.ciudad,
            "provincia": direccion.provincia,
            "codigo_postal": direccion.codigo_postal,
            "telefono_contacto": direccion.telefono_contacto,
        }, ensure_ascii=False)

    async def _decrement_stock(self, producto_id: int, cantidad: int) -> None:
        result = await self.db.execute(
            select(Producto).where(Producto.id == producto_id).with_for_update()
        )
        producto = result.scalar_one_or_none()
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto {producto_id} no encontrado",
            )
        if getattr(producto, 'stock_cantidad', 1) is not None and producto.stock_cantidad < cantidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente para '{producto.nombre}': disponible {producto.stock_cantidad}, requerido {cantidad}",
            )
        if hasattr(producto, 'stock_cantidad') and producto.stock_cantidad is not None:
            producto.stock_cantidad -= cantidad
            await self.db.flush()

    async def _restore_stock(self, producto_id: int, cantidad: int) -> None:
        result = await self.db.execute(
            select(Producto).where(Producto.id == producto_id).with_for_update()
        )
        producto = result.scalar_one_or_none()
        if producto and hasattr(producto, 'stock_cantidad') and producto.stock_cantidad is not None:
            producto.stock_cantidad += cantidad
            await self.db.flush()

    async def create(self, data: PedidoCreate, usuario_id: int) -> Pedido:
        """Create a new pedido with items, snapshot, and historial."""
        if not data.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El pedido debe tener al menos un item",
            )

        total = sum(item.cantidad * item.precio_unitario for item in data.items)

        # Capture address snapshot
        direccion_snapshot = await self._capture_direccion_snapshot(data.direccion_id)

        pedido = Pedido(
            usuario_id=usuario_id,
            estado="PENDIENTE",
            total=total,
            direccion_id=data.direccion_id,
            direccion_snapshot=direccion_snapshot,
            forma_pago_id=data.forma_pago_id,
        )

        created = await self.repo.create(pedido)

        for item_data in data.items:
            item = PedidoItem(
                pedido_id=created.id,
                producto_id=item_data.producto_id,
                producto_nombre=item_data.producto_nombre,
                cantidad=item_data.cantidad,
                precio_unitario=item_data.precio_unitario,
                subtotal=item_data.cantidad * item_data.precio_unitario,
            )
            await self.repo.create_pedido_item(item)

        # Record initial historial
        await self._create_historial(
            pedido_id=created.id,
            estado_hasta="PENDIENTE",
            usuario_id=usuario_id,
            observacion="Pedido creado",
        )

        return await self.repo.get_pedido_with_items(created.id)

    async def get_user_pedidos(
        self, usuario_id: int, page: int = 1, size: int = 20
    ) -> dict:
        skip = (page - 1) * size
        items = await self.repo.get_user_pedidos(usuario_id, skip=skip, limit=size)
        total = await self.repo.count_user_pedidos(usuario_id)
        return {"items": items, "total": total, "page": page, "size": size}

    async def get_all_pedidos(
        self, page: int = 1, size: int = 20
    ) -> dict:
        skip = (page - 1) * size
        items = await self.repo.get_all_pedidos(skip=skip, limit=size)
        total = await self.repo.count_all_pedidos()
        return {"items": items, "total": total, "page": page, "size": size}

    async def get_by_id(self, pedido_id: int, usuario_id: int, is_admin: bool = False) -> Pedido:
        pedido = await self.repo.get_pedido_with_items(pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )
        if not is_admin and pedido.usuario_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )
        return pedido

    async def update_estado(
        self,
        pedido_id: int,
        data: PedidoEstadoUpdate,
        usuario: Usuario,
    ) -> Pedido:
        """Update pedido estado with FSM and role validation.

        Validates the state transition is:
        1. Allowed by the FSM (can_transition)
        2. Permitted for at least one of the user's roles (ROLE_TRANSITIONS)

        Emits a kitchen event if the event_manager is configured.
        """
        pedido = await self.repo.get_by_id_raw(pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )

        target = data.estado.upper()
        if not can_transition(pedido.estado, target):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede cambiar de '{pedido.estado}' a '{target}'",
            )

        from_state = pedido.estado

        # Role-based transition validation
        role_names = self._get_role_names(usuario)
        self._validate_role_transition(role_names, from_state, target)

        # Stock management
        if from_state == "PENDIENTE" and target == "CONFIRMADO":
            items = await self.repo.get_pedido_with_items(pedido_id)
            for item in items.items:
                await self._decrement_stock(item.producto_id, item.cantidad)

        if from_state == "CONFIRMADO" and target == "CANCELADO":
            items = await self.repo.get_pedido_with_items(pedido_id)
            for item in items.items:
                await self._restore_stock(item.producto_id, item.cantidad)

        pedido.estado = target
        pedido.actualizado_en = datetime.now(timezone.utc)
        updated = await self.repo.update(pedido)

        # Record historial
        await self._create_historial(
            pedido_id=pedido_id,
            estado_desde=from_state,
            estado_hasta=target,
            usuario_id=usuario.id,
            observacion=f"Transición: {from_state} → {target}",
        )

        # Emit kitchen event if event_manager is configured
        if self.event_manager and from_state != target:
            await self._emit_kitchen_event(from_state, target, pedido)

        return await self.repo.get_pedido_with_items(pedido_id)

    async def _emit_kitchen_event(
        self, from_state: str, target: str, pedido: Pedido,
    ) -> None:
        """Emit a kitchen event based on the state transition."""
        # Determine event type
        event_type = None
        if from_state == "PENDIENTE" and target == "CONFIRMADO":
            event_type = "PEDIDO_CONFIRMADO"
        elif from_state == "CONFIRMADO" and target == "EN_PREPARACION":
            event_type = "PEDIDO_EN_PREPARACION"
        elif from_state == "EN_PREPARACION" and target == "EN_CAMINO":
            event_type = "PEDIDO_EN_CAMINO"
        elif target == "CANCELADO" and from_state in ("CONFIRMADO", "EN_PREPARACION"):
            event_type = "PEDIDO_CANCELADO"

        if event_type:
            event = KitchenEvent(
                type=event_type,
                pedido_id=pedido.id,
                data={
                    "pedido_id": pedido.id,
                    "estado": target,
                    "from_state": from_state,
                },
            )
            await self.event_manager.broadcast(EventManager.CHANNEL_KITCHEN, event)
