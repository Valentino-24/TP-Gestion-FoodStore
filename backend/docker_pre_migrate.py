"""Create seed tables (rol, estado_pedido, forma_pago) before running Alembic migrations.

These tables are defined as SQLModel models but have no Alembic migration.
They must exist before the initial migration runs (usuario_rol FK references rol).
"""

import asyncio
from sqlmodel import SQLModel

from app.database import engine
from app.models.rol import Rol
from app.models.estado_pedido import EstadoPedido
from app.models.forma_pago import FormaPago


async def main() -> None:
    """Create seed tables if they don't exist."""
    tables = [Rol.__table__, EstadoPedido.__table__, FormaPago.__table__]
    async with engine.begin() as conn:
        for table in tables:
            await conn.run_sync(lambda sync_conn: table.create(sync_conn, checkfirst=True))
            print(f"Table '{table.name}' created (or already exists).")


if __name__ == "__main__":
    asyncio.run(main())
