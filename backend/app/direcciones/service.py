"""Direcciones service — business logic for user addresses."""

from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.direcciones.repository import DireccionRepository
from app.direcciones.schemas import DireccionCreate, DireccionUpdate
from app.models.direccion import Direccion


class DireccionService:
    """Service layer for address management."""

    def __init__(self, repo: DireccionRepository):
        """Initialize with repository dependency."""
        self.repo = repo

    async def create(self, data: DireccionCreate, usuario_id: int) -> Direccion:
        """Create a new address for a user.

        Args:
            data: Address creation data.
            usuario_id: The authenticated user's ID.

        Returns:
            The created address.
        """
        direccion = Direccion(
            usuario_id=usuario_id,
            calle=data.calle,
            numero=data.numero,
            ciudad=data.ciudad,
            provincia=data.provincia,
            codigo_postal=data.codigo_postal,
            telefono_contacto=data.telefono_contacto,
            activo=True,
        )
        return await self.repo.create(direccion)

    async def get_all(self, usuario_id: int) -> list[Direccion]:
        """Get all active addresses for a user.

        Args:
            usuario_id: The authenticated user's ID.

        Returns:
            List of active addresses.
        """
        return await self.repo.get_user_addresses(usuario_id)

    async def get_by_id(self, address_id: int, usuario_id: int) -> Direccion:
        """Get a single address by ID, scoped to user.

        Args:
            address_id: The address ID.
            usuario_id: The authenticated user's ID.

        Returns:
            The address.

        Raises:
            HTTPException 404: If address not found or not owned by user.
        """
        direccion = await self.repo.get_user_address_by_id(address_id, usuario_id)
        if not direccion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dirección no encontrada",
            )
        return direccion

    async def update(self, address_id: int, data: DireccionUpdate, usuario_id: int) -> Direccion:
        """Update an address.

        Args:
            address_id: The address ID.
            data: Fields to update.
            usuario_id: The authenticated user's ID.

        Returns:
            The updated address.

        Raises:
            HTTPException 404: If address not found or not owned by user.
        """
        direccion = await self.get_by_id(address_id, usuario_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(direccion, field, value)

        direccion.actualizado_en = datetime.now(timezone.utc)
        return await self.repo.update(direccion)

    async def delete(self, address_id: int, usuario_id: int) -> None:
        """Soft-delete an address.

        Args:
            address_id: The address ID.
            usuario_id: The authenticated user's ID.

        Raises:
            HTTPException 404: If address not found or not owned by user.
        """
        direccion = await self.get_by_id(address_id, usuario_id)
        direccion.activo = False
        direccion.actualizado_en = datetime.now(timezone.utc)
        await self.repo.update(direccion)
