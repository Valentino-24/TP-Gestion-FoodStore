"""Unit of Work pattern for atomic database operations."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker


class UnitOfWork:
    """Unit of Work for atomic multi-table database operations.
    
    Usage:
        async def create_order_with_stock(uow: UnitOfWork):
            async with uow:
                order = await uow.orders.create(...)
                await uow.products.update_stock(...)
    """
    
    def __init__(self):
        """Initialize UoW with session maker."""
        self._session_maker = async_session_maker
    
    @asynccontextmanager
    async def __call__(self) -> Async_generator[AsyncSession, None]:
        """Context manager for UoW.
        
        Yields:
            AsyncSession for database operations
        """
        async with self._session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def __aenter__(self):
        """Async context entry."""
        self.session = await self._session_maker().__aenter__()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context exit with commit/rollback."""
        if exc_type is None:
            await self.session.commit()
        else:
            await self.session.rollback()
        await self.session.close()