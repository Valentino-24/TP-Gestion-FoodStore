"""Database connection and SQLModel configuration."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel

from app.config import settings


# Alias for backward compatibility — all models use SQLModel as base
Base = SQLModel

# Set naming convention to match the one Alembic used when generating migrations.
# This ensures constraint names are consistent whether tables are created via
# SQLModel (e.g., docker_pre_migrate.py) or via Alembic migrations.
# 
# Without this, seed tables created by docker_pre_migrate.py get auto-generated
# constraint names that DON'T match what the Alembic migrations expect, causing
# failures like:
#   constraint "estado_pedido_nombre_key" of relation "estado_pedido" does not exist
_naming_convention = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}
Base.metadata.naming_convention = _naming_convention


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """Dependency that provides a database session.
    
    Yields:
        AsyncSession: Database session
        
    Example:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
