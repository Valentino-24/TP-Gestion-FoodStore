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

CATEGORIAS = [
    (1, "Bebidas", "Aguas, gaseosas, jugos y bebidas alcoholicas"),
    (2, "Comidas", "Platos preparados, comidas al paso y menus ejecutivos"),
    (3, "Snacks", "Picadas, papas fritas, frutos secos y bocaditos"),
    (4, "Postres", "Dulces, pasteleria, helados y reposteria"),
    (5, "Otros", "Productos que no encajan en las categorias anteriores"),
]

CLIENTES = [
    (1, "Carlos", "Garcia", "carlos.garcia@email.com", "1123456789", "Av. Corrientes 1234, CABA"),
    (2, "Maria", "Lopez", "maria.lopez@email.com", "1198765432", "Calle Florida 567, CABA"),
    (3, "Juan", "Martinez", "juan.martinez@email.com", "1144556677", "Av. Santa Fe 890, CABA"),
]

PRODUCTOS = [
    (1, "Coca-Cola", "Gaseosa sabor cola 500ml", 2.50, 1),
    (2, "Agua", "Agua mineral sin gas 500ml", 1.00, 1),
    (3, "Jugo de Naranja", "Jugo de naranja natural exprimido 400ml", 3.00, 1),
    (4, "Hamburguesa", "Hamburguesa completa con cheddar y bacon", 8.50, 2),
    (5, "Pizza", "Pizza de mozzarella por porcion", 12.00, 2),
    (6, "Ensalada", "Ensalada mixta con pollo y vegetales frescos", 7.50, 2),
    (7, "Papas Fritas", "Papas fritas crocantes porcion mediana", 3.50, 3),
    (8, "Nachos", "Nachos con queso cheddar y guacamole", 4.00, 3),
    (9, "Barrita de cereal", "Barrita de cereal con chocolate", 1.50, 3),
    (10, "Helado", "Helado artesanal 2 bochas", 4.50, 4),
    (11, "Flan", "Flan casero con dulce de leche", 3.00, 4),
    (12, "Brownie", "Brownie de chocolate con nueces", 2.50, 4),
    (13, "Salsa de tomate", "Salsa de tomate para acompaniar", 1.00, 5),
    (14, "Mayonesa", "Mayonesa clasica 100g", 1.00, 5),
    (15, "Aderezo", "Aderezo criollo para empanadas", 1.50, 5),
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


def seed_categorias(conn):
    """Seed Categoria table."""
    with conn.begin():
        for cat in CATEGORIAS:
            conn.execute(text("""
                INSERT INTO categoria (id, nombre, descripcion, activo)
                VALUES (:id, :nombre, :descripcion, TRUE)
                ON CONFLICT (id) DO NOTHING
            """), {"id": cat[0], "nombre": cat[1], "descripcion": cat[2]})


def seed_productos(conn):
    """Seed Producto table."""
    with conn.begin():
        for prod in PRODUCTOS:
            conn.execute(text("""
                INSERT INTO producto (id, nombre, descripcion, precio, categoria_id, activo)
                VALUES (:id, :nombre, :descripcion, :precio, :categoria_id, TRUE)
                ON CONFLICT (id) DO NOTHING
            """), {"id": prod[0], "nombre": prod[1], "descripcion": prod[2], "precio": prod[3], "categoria_id": prod[4]})


def seed_clientes(conn):
    """Seed Cliente table."""
    with conn.begin():
        for cli in CLIENTES:
            conn.execute(text("""
                INSERT INTO cliente (id, nombre, apellido, email, telefono, direccion, activo)
                VALUES (:id, :nombre, :apellido, :email, :telefono, :direccion, TRUE)
                ON CONFLICT (id) DO NOTHING
            """), {"id": cli[0], "nombre": cli[1], "apellido": cli[2], "email": cli[3], "telefono": cli[4], "direccion": cli[5]})


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

        with engine.connect() as conn:
            seed_categorias(conn)
        print("✓ Seeded categorias")

        with engine.connect() as conn:
            seed_productos(conn)
        print("✓ Seeded productos")

        with engine.connect() as conn:
            seed_clientes(conn)
        print("✓ Seeded clientes")

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
