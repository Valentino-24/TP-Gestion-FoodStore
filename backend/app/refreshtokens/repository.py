"""RefreshTokens repository — token data access."""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Repository for RefreshToken with security-specific queries."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, RefreshToken)

    async def get_by_token_hash(self, token_hash: str) -> Optional[RefreshToken]:
        """Get a refresh token by its SHA-256 hash.

        Args:
            token_hash: The SHA-256 hex digest of the token.

        Returns:
            RefreshToken if found, None otherwise.
        """
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_by_user(self, user_id: int) -> List[RefreshToken]:
        """Get all non-revoked, non-expired refresh tokens for a user.

        Args:
            user_id: The user ID.

        Returns:
            List of active RefreshToken records.
        """
        now = datetime.utcnow()
        stmt = (
            select(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > now,
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def revoke_all_by_user(self, user_id: int) -> int:
        """Revoke all refresh tokens for a user (for replay attack response).

        Args:
            user_id: The user ID whose tokens should be revoked.

        Returns:
            Number of tokens revoked.
        """
        now = datetime.utcnow()
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )
        result = await self.db.execute(stmt)
        return result.rowcount

    async def revoke_by_family(self, family_id: str) -> int:
        """Revoke all refresh tokens in a family (for replay attack response).

        Args:
            family_id: The family ID whose tokens should be revoked.

        Returns:
            Number of tokens revoked.
        """
        now = datetime.utcnow()
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.family_id == family_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )
        result = await self.db.execute(stmt)
        return result.rowcount
