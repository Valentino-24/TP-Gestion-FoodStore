"""Database seed script for initial reference data.

Uses SQLAlchemy sync engine to avoid encoding issues.
Reads DATABASE_URL from .env via app config (converts async URL to sync).
"""

import sys
import os

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine, text


# Seed data constants
ROLES = [
    (1, "ADMIN", "Administrador con acceso total"),
    (2, "STOCK", "Gestor de stock e inventario"),
    (3, "PEDIDOS", "Gestor de pedidos"),
    (4, "CLIENT", "Cliente final"),
]

ESTADOS_PEDIDO = [
    (1, "PENDIENTE", "Esperando confirmacion de pago"),
    (2, "CONFIRMADO", "Pago confirmado, listo para preparar"),
    (3, "EN_PREPARACION", "Preparando el pedido"),
    (4, "EN_CAMINO", "Enviado al cliente"),
    (5, "ENTREGADO", "Entregado al cliente"),
    (6, "CANCELADO", "Pedido cancelado"),
]

FORMAS_PAGO = [
    (1, "Tarjeta de credito", True),
    (2, "Tarjeta de debito", True),
]


def get_sync_url(async_url: str) -> str:
    """Convert an async database URL to a sync one.

    Examples:
        postgresql+asyncpg://... -> postgresql://...
    """
    return async_url.replace("postgresql+asyncpg", "postgresql")


def create_tables(conn):
    """Create tables if they don't exist."""
    with conn.begin():
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS rol (
                id INTEGER PRIMARY KEY,
                nombre VARCHAR(100) UNIQUE NOT NULL,
                descripcion TEXT
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS estado_pedido (
                id INTEGER PRIMARY KEY,
                nombre VARCHAR(100) UNIQUE NOT NULL,
                descripcion TEXT
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS forma_pago (
                id INTEGER PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                activo BOOLEAN DEFAULT TRUE
            )
        """))


def seed_roles(conn):
    """Seed Roles table."""
    with conn.begin():
        for rol in ROLES:
            conn.execute(text("""
                INSERT INTO rol (id, nombre, descripcion)
                VALUES (:id, :nombre, :descripcion)
                ON CONFLICT (id) DO NOTHING
            """), {"id": rol[0], "nombre": rol[1], "descripcion": rol[2]})


def seed_estados_pedido(conn):
    """Seed EstadosPedido table."""
    with conn.begin():
        for estado in ESTADOS_PEDIDO:
            conn.execute(text("""
                INSERT INTO estado_pedido (id, nombre, descripcion)
                VALUES (:id, :nombre, :descripcion)
                ON CONFLICT (id) DO NOTHING
            """), {"id": estado[0], "nombre": estado[1], "descripcion": estado[2]})


def seed_formas_pago(conn):
    """Seed FormasPago table."""
    with conn.begin():
        for forma in FORMAS_PAGO:
            conn.execute(text("""
                INSERT INTO forma_pago (id, nombre, activo)
                VALUES (:id, :nombre, :activo)
                ON CONFLICT (id) DO NOTHING
            """), {"id": forma[0], "nombre": forma[1], "activo": forma[2]})


def run_seed():
    """Run all seeds."""
    # Read DATABASE_URL from environment (same as app config uses)
    from app.config import settings

    db_url = get_sync_url(settings.DATABASE_URL)
    engine = create_engine(db_url)

    try:
        # Create tables
        with engine.connect() as conn:
            create_tables(conn)
        print("✓ Tables created")

        # Seed data
        with engine.connect() as conn:
            seed_roles(conn)
        print("✓ Seeded roles")

        with engine.connect() as conn:
            seed_estados_pedido(conn)
        print("✓ Seeded estados_pedido")

        with engine.connect() as conn:
            seed_formas_pago(conn)
        print("✓ Seeded formas_pago")

        # Verify
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, nombre FROM rol ORDER BY id"))
            roles = result.fetchall()
            print(f"✓ Roles: {roles}")

        print("\n✓ Seed completed successfully!")

    finally:
        engine.dispose()


if __name__ == "__main__":
    run_seed()
