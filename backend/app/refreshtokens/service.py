"""RefreshToken service — token lifecycle with replay detection."""

import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple

from fastapi import HTTPException, status

from app.config import settings
from app.models.refresh_token import RefreshToken
from app.refreshtokens.repository import RefreshTokenRepository

# Generic error for expired/revoked tokens
INVALID_TOKEN_ERROR = "Token de refresco invalido o expirado"


class RefreshTokenService:
    """Manages refresh token creation, rotation, and revocation.

    Security model:
    - Tokens are UUID v4, stored as SHA-256 hash in DB
    - Each token has a family_id for rotation tracking
    - Replay detection: if a used token is reused, revoke all family tokens
    """

    def __init__(self, repo: RefreshTokenRepository):
        self.repo = repo

    def create_token(self, user_id: int) -> Tuple[str, str]:
        """Create a new refresh token for a user.

        Args:
            user_id: The user to create the token for.

        Returns:
            Tuple of (plain_token_for_client, family_id).
            The plain token is NEVER stored — only its SHA-256 hash.
        """
        plain_token = str(uuid.uuid4())
        token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
        family_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        record = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            family_id=family_id,
        )
        # Note: caller must add to session and commit
        self.repo.db.add(record)
        self.repo.db.flush()

        return plain_token, family_id

    async def rotate_token(self, old_plain_token: str) -> Tuple[str, RefreshToken]:
        """Rotate a refresh token: invalidate old, issue new.

        Implements replay attack detection: if the old token was already
        revoked, all tokens in its family are revoked.

        Args:
            old_plain_token: The refresh token to rotate.

        Returns:
            Tuple of (new_plain_token, old_token_record).

        Raises:
            HTTPException 401 if token is expired or invalid.
        """
        old_hash = hashlib.sha256(old_plain_token.encode()).hexdigest()
        old_record = await self.repo.get_by_token_hash(old_hash)

        if old_record is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=INVALID_TOKEN_ERROR,
            )

        # Check if token is expired
        if old_record.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de refresco expirado",
            )

        # Check if already revoked → REPLAY ATTACK DETECTION
        if old_record.revoked_at is not None:
            await self._handle_replay_attack(old_record.family_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de refresco invalido o expirado",
            )

        # Revoke the old token
        old_record.revoked_at = datetime.utcnow()
        await self.repo.db.flush()

        # Create new token in the SAME family
        new_plain_token = self._create_for_family(
            old_record.user_id, old_record.family_id
        )

        return new_plain_token, old_record

    async def revoke_token(self, plain_token: str) -> None:
        """Revoke a refresh token (logout).

        Idempotent: if token doesn't exist or is already revoked, no error.

        Args:
            plain_token: The refresh token to revoke.
        """
        token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
        record = await self.repo.get_by_token_hash(token_hash)
        if record is not None and record.revoked_at is None:
            record.revoked_at = datetime.utcnow()
            await self.repo.db.flush()

    async def _handle_replay_attack(self, family_id: str) -> None:
        """Revoke all tokens in a family when replay attack is detected.

        Args:
            family_id: The family whose tokens should be revoked.
        """
        await self.repo.revoke_by_family(family_id)

    def _create_for_family(self, user_id: int, family_id: str) -> str:
        """Create a new refresh token within an existing family.

        Args:
            user_id: The user to create the token for.
            family_id: The family ID to associate with.

        Returns:
            Plain token string for the client.
        """
        plain_token = str(uuid.uuid4())
        token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        record = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            family_id=family_id,
        )
        self.repo.db.add(record)
        self.repo.db.flush()

        return plain_token
