## Why

The FoodStore needs a product catalog to list items for sale. Products are the core entity of the system — orders, payments, and inventory all revolve around them. This change builds the product CRUD on top of the categorias module (us-002), adding the categoria_id foreign key relationship.

## What Changes

- Create `Producto` model with id, nombre, descripcion, precio, categoria_id (FK → categoria), imagen_url, activo, creado_en, actualizado_en
- Implement full CRUD REST API for products under `/api/v1/productos`
- Admin-only write operations (create, update, delete); authenticated users can read
- Filter products by categoria_id
- Pagination support for product listing
- Generate Alembic migration for the producto table
- Link product model to categoria via foreign key (cascade on categoria soft-delete does not apply)

## Capabilities

### New Capabilities
- `productos`: Product catalog management — CRUD operations for managing food products with category association

### Modified Capabilities
- `categorias`: No requirement changes. Products reference existing categories without modifying category behavior.

## Impact

- **New model**: `backend/app/models/producto.py`
- **New routes**: `/api/v1/productos` — GET (list with pagination + category filter), GET /{id} (detail), POST (create), PUT /{id} (update), DELETE /{id} (soft delete via activo flag)
- **Dependencies**: Requires categorias (us-002) for categoria_id FK; auth (us-001) for role-based access
- **DB migration**: New `producto` table with FK to `categoria`
- **DB index**: Index on categoria_id for filtered queries
