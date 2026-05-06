"""Auth repository — Usuario data access."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.usuario import Usuario
from app.repositories.base import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    """Repository for Usuario with auth-specific queries."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Usuario)

    async def get_by_email(self, email: str) -> Optional[Usuario]:
        """Get a user by email, excluding soft-deleted users.

        Args:
            email: The email address to look up.

        Returns:
            Usuario if found and not deleted, None otherwise.
        """
        stmt = (
            select(Usuario)
            .where(Usuario.email == email, Usuario.eliminado_en.is_(None))
            .options(selectinload(Usuario.roles))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_roles(self, user_id: int) -> Optional[Usuario]:
        """Get a user by ID with roles eagerly loaded.

        Args:
            user_id: The user ID to look up.

        Returns:
            Usuario with roles loaded, or None.
        """
        stmt = (
            select(Usuario)
            .where(Usuario.id == user_id, Usuario.eliminado_en.is_(None))
            .options(selectinload(Usuario.roles))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
