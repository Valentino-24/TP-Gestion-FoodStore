"""Database seed using pg8000."""

import pg8000.native

print("Testing with pg8000...")

conn = pg8000.native.Connection(
    user="postgres",
    password="admin",
    host="localhost",
    database="foodstore"
)
print("Connected!")

# Seed roles - using simple string interpolation
conn.run("""
    INSERT INTO rol (id, nombre, descripcion) VALUES (1, 'ADMIN', 'Administrador con acceso total') ON CONFLICT (id) DO NOTHING
""")
conn.run("""
    INSERT INTO rol (id, nombre, descripcion) VALUES (2, 'STOCK', 'Gestor de stock e inventario') ON CONFLICT (id) DO NOTHING
""")
conn.run("""
    INSERT INTO rol (id, nombre, descripcion) VALUES (3, 'PEDIDOS', 'Gestor de pedidos') ON CONFLICT (id) DO NOTHING
""")
conn.run("""
    INSERT INTO rol (id, nombre, descripcion) VALUES (4, 'CLIENT', 'Cliente final') ON CONFLICT (id) DO NOTHING
""")
print("Roles seeded")

# Seed estados
estados = [
    ("PENDIENTE", "Esperando confirmacion de pago"),
    ("CONFIRMADO", "Pago confirmado, listo para preparar"),
    ("EN_PREPARACION", "Preparando el pedido"),
    ("EN_CAMINO", "Enviado al cliente"),
    ("ENTREGADO", "Entregado al cliente"),
    ("CANCELADO", "Pedido cancelado"),
]
for i, (nombre, desc) in enumerate(estados, 1):
    conn.run(f"INSERT INTO estado_pedido (id, nombre, descripcion) VALUES ({i}, '{nombre}', '{desc}') ON CONFLICT (id) DO NOTHING")
print("Estados seeded")

# Seed formas_pago
conn.run("INSERT INTO forma_pago (id, nombre, activo) VALUES (1, 'Tarjeta de credito', true) ON CONFLICT (id) DO NOTHING")
conn.run("INSERT INTO forma_pago (id, nombre, activo) VALUES (2, 'Tarjeta de debito', true) ON CONFLICT (id) DO NOTHING")
print("Formas pago seeded")

# Verify
result = conn.run("SELECT * FROM rol ORDER BY id")
print("\nRoles:", result)

result = conn.run("SELECT * FROM estado_pedido ORDER BY id")
print("Estados:", result)

result = conn.run("SELECT * FROM forma_pago ORDER BY id")
print("Formas:", result)

conn.close()
print("\nSeed completed!")