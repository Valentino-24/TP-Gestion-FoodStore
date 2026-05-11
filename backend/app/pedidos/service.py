"""Pedidos service — business logic with FSM state management."""

from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.models.pedido import Pedido, can_transition
from app.models.pedido_item import PedidoItem
from app.pedidos.repository import PedidoRepository
from app.pedidos.schemas import PedidoCreate, PedidoEstadoUpdate


class PedidoService:
    """Service layer for order management with FSM."""

    def __init__(self, repo: PedidoRepository):
        """Initialize with repository dependency."""
        self.repo = repo

    async def create(self, data: PedidoCreate, usuario_id: int) -> Pedido:
        """Create a new pedido with items and calculate total.

        Args:
            data: Pedido creation data with items.
            usuario_id: The authenticated user's ID.

        Returns:
            The created pedido with items.

        Raises:
            HTTPException 400: If no items provided.
        """
        if not data.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El pedido debe tener al menos un item",
            )

        # Calculate total from items
        total = sum(item.cantidad * item.precio_unitario for item in data.items)

        pedido = Pedido(
            usuario_id=usuario_id,
            estado="PENDIENTE",
            total=total,
            direccion_id=data.direccion_id,
            forma_pago_id=data.forma_pago_id,
        )

        created = await self.repo.create(pedido)

        # Create items
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

        # Re-fetch with items
        return await self.repo.get_pedido_with_items(created.id)

    async def get_user_pedidos(
        self, usuario_id: int, page: int = 1, size: int = 20
    ) -> dict:
        """Get paginated pedidos for a user.

        Args:
            usuario_id: The user ID.
            page: Page number (1-indexed).
            size: Items per page.

        Returns:
            Dict with items, total, page, size.
        """
        skip = (page - 1) * size
        items = await self.repo.get_user_pedidos(usuario_id, skip=skip, limit=size)
        total = await self.repo.count_user_pedidos(usuario_id)
        return {"items": items, "total": total, "page": page, "size": size}

    async def get_all_pedidos(
        self, page: int = 1, size: int = 20
    ) -> dict:
        """Get all pedidos paginated (admin).

        Args:
            page: Page number (1-indexed).
            size: Items per page.

        Returns:
            Dict with items, total, page, size.
        """
        skip = (page - 1) * size
        items = await self.repo.get_all_pedidos(skip=skip, limit=size)
        total = await self.repo.count_all_pedidos()
        return {"items": items, "total": total, "page": page, "size": size}

    async def get_by_id(self, pedido_id: int, usuario_id: int, is_admin: bool = False) -> Pedido:
        """Get a pedido by ID.

        Args:
            pedido_id: The pedido ID.
            usuario_id: The authenticated user's ID (for scoping).
            is_admin: Whether the user is admin (bypasses ownership check).

        Returns:
            The pedido with items.

        Raises:
            HTTPException 404: If not found or not owned by user.
        """
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
        self, pedido_id: int, data: PedidoEstadoUpdate
    ) -> Pedido:
        """Update pedido estado with FSM validation (admin only).

        Args:
            pedido_id: The pedido ID.
            data: Target estado.

        Returns:
            The updated pedido.

        Raises:
            HTTPException 400: If state transition is invalid.
            HTTPException 404: If pedido not found.
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

        pedido.estado = target
        pedido.actualizado_en = datetime.now(timezone.utc)
        return await self.repo.update(pedido)
