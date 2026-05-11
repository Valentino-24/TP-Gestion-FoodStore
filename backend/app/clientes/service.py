"""Cliente service — business logic for customer management."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status

from app.database import AsyncSession
from app.models.cliente import Cliente
from app.clientes.repository import ClienteRepository
from app.clientes.schemas import ClienteCreate, ClienteUpdate


class ClienteService:
    """Service layer for customer management."""

    def __init__(self, repo: ClienteRepository, db: AsyncSession):
        """Initialize with repository and db dependencies."""
        self.repo = repo
        self.db = db

    async def _validate_unique_email(
        self, email: str, exclude_id: Optional[int] = None
    ) -> None:
        """Check that the email is not already in use by another customer.

        Args:
            email: The email to validate.
            exclude_id: Optional customer ID to exclude from the check (for updates).

        Raises:
            HTTPException 422: If the email is already registered.
        """
        existing = await self.repo.get_by_email(email)
        if existing and (exclude_id is None or existing.id != exclude_id):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El email ya se encuentra registrado",
            )

    async def create(self, data: ClienteCreate) -> Cliente:
        """Create a new customer.

        Args:
            data: Customer creation data.

        Returns:
            The created customer.

        Raises:
            HTTPException 422: If the email is already registered.
        """
        await self._validate_unique_email(data.email)

        cliente = Cliente(
            nombre=data.nombre,
            apellido=data.apellido,
            email=data.email,
            telefono=data.telefono,
            direccion=data.direccion,
            activo=True,
        )
        return await self.repo.create(cliente)

    async def get_all(
        self,
        page: int = 1,
        size: int = 20,
    ) -> dict:
        """Get paginated list of active customers.

        Args:
            page: Page number (1-indexed).
            size: Items per page.

        Returns:
            Dict with items, total, page, size.
        """
        skip = (page - 1) * size
        items = await self.repo.get_active(skip=skip, limit=size)
        total = await self.repo.count_active()

        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
        }

    async def get_by_id(self, cliente_id: int) -> Cliente:
        """Get a single active customer by ID.

        Args:
            cliente_id: The customer ID.

        Returns:
            The customer.

        Raises:
            HTTPException 404: If customer not found or inactive.
        """
        cliente = await self.repo.get_by_id(cliente_id)
        if not cliente or not cliente.activo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado",
            )
        return cliente

    async def update(self, cliente_id: int, data: ClienteUpdate) -> Cliente:
        """Update a customer.

        Args:
            cliente_id: The customer ID to update.
            data: Fields to update.

        Returns:
            The updated customer.

        Raises:
            HTTPException 404: If customer not found.
            HTTPException 422: If the new email is already in use.
        """
        cliente = await self.repo.get_by_id(cliente_id)
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado",
            )

        # Validate email uniqueness if changing it
        if data.email is not None and data.email != cliente.email:
            await self._validate_unique_email(data.email, exclude_id=cliente_id)

        # Apply updates (only provided fields)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(cliente, field, value)

        cliente.actualizado_en = datetime.now(timezone.utc)
        return await self.repo.update(cliente)

    async def delete(self, cliente_id: int) -> None:
        """Soft-delete a customer by setting activo=False.

        Args:
            cliente_id: The customer ID to delete.

        Raises:
            HTTPException 404: If customer not found.
        """
        cliente = await self.repo.get_by_id(cliente_id)
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado",
            )

        cliente.activo = False
        cliente.actualizado_en = datetime.now(timezone.utc)
        await self.repo.update(cliente)

    async def get_by_email(self, email: str) -> Optional[Cliente]:
        """Get a customer by email.

        Used for CLIENT role self-lookup (email-based binding).

        Args:
            email: The customer email.

        Returns:
            The customer if found, None otherwise.
        """
        return await self.repo.get_by_email(email)
