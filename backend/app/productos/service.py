"""Producto service — business logic for food products."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select

from app.database import AsyncSession
from app.models.categoria import Categoria
from app.models.producto import Producto
from app.productos.repository import ProductoRepository
from app.productos.schemas import ProductoCreate, ProductoUpdate


class ProductoService:
    """Service layer for product management."""

    def __init__(self, repo: ProductoRepository, db: AsyncSession):
        """Initialize with repository and db dependencies."""
        self.repo = repo
        self.db = db

    async def _validate_categoria(self, categoria_id: int) -> None:
        """Check that a categoria_id references an existing category.

        Args:
            categoria_id: The category ID to validate.

        Raises:
            HTTPException 404: If category not found.
        """
        result = await self.db.execute(
            select(Categoria).where(Categoria.id == categoria_id)
        )
        categoria = result.scalar_one_or_none()
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria no encontrada",
            )

    async def create(self, data: ProductoCreate) -> Producto:
        """Create a new product.

        Args:
            data: Product creation data.

        Returns:
            The created product.

        Raises:
            HTTPException 404: If categoria_id does not exist.
        """
        await self._validate_categoria(data.categoria_id)

        producto = Producto(
            nombre=data.nombre,
            descripcion=data.descripcion,
            precio=data.precio,
            categoria_id=data.categoria_id,
            imagen_url=data.imagen_url,
            activo=True,
        )
        return await self.repo.create(producto)

    async def get_all(
        self,
        page: int = 1,
        size: int = 20,
        categoria_id: Optional[int] = None,
    ) -> dict:
        """Get paginated list of active products.

        Args:
            page: Page number (1-indexed).
            size: Items per page.
            categoria_id: Optional category filter.

        Returns:
            Dict with items, total, page, size.
        """
        skip = (page - 1) * size
        items = await self.repo.get_active(skip=skip, limit=size, categoria_id=categoria_id)
        total = await self.repo.count_active(categoria_id=categoria_id)

        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
        }

    async def get_by_id(self, producto_id: int) -> Producto:
        """Get a single active product by ID.

        Args:
            producto_id: The product ID.

        Returns:
            The product.

        Raises:
            HTTPException 404: If product not found or inactive.
        """
        producto = await self.repo.get_by_id(producto_id)
        if not producto or not producto.activo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado",
            )
        return producto

    async def update(self, producto_id: int, data: ProductoUpdate) -> Producto:
        """Update a product.

        Args:
            producto_id: The product ID to update.
            data: Fields to update.

        Returns:
            The updated product.

        Raises:
            HTTPException 404: If product not found or categoria_id does not exist.
        """
        producto = await self.repo.get_by_id(producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado",
            )

        # Validate categoria_id if changing it
        if data.categoria_id is not None and data.categoria_id != producto.categoria_id:
            await self._validate_categoria(data.categoria_id)

        # Apply updates (only provided fields)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(producto, field, value)

        producto.actualizado_en = datetime.now(timezone.utc)
        return await self.repo.update(producto)

    async def delete(self, producto_id: int) -> None:
        """Soft-delete a product by setting activo=False.

        Args:
            producto_id: The product ID to delete.

        Raises:
            HTTPException 404: If product not found.
        """
        producto = await self.repo.get_by_id(producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado",
            )

        producto.activo = False
        producto.actualizado_en = datetime.now(timezone.utc)
        await self.repo.update(producto)
