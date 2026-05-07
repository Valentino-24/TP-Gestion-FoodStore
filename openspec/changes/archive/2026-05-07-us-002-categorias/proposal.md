## Why

The FoodStore needs product categorization to organize inventory. Categories enable customers to browse by department and admins to manage stock structure. This is a prerequisite for the productos module (us-003).

## What Changes

- Create `Categoria` model with id, nombre (unique, indexed), descripcion, activo
- Implement full CRUD REST API for categories under `/api/v1/categorias`
- Admin-only write operations (create, update, delete); authenticated users can read
- Add seed data with initial categories (Bebidas, Comidas, Snacks, etc.)
- Generate Alembic migration for the categoria table

## Capabilities

### New Capabilities
- `categorias`: Product category management — CRUD operations for organizing products into categories

### Modified Capabilities

<!-- No existing capabilities are modified -->

## Impact

- **New model**: `backend/app/models/categoria.py`
- **New routes**: `/api/v1/categorias` — GET (list), GET /{id} (detail), POST (create), PUT /{id} (update), DELETE /{id} (soft delete via activo flag)
- **Dependencies**: Requires auth module (us-001-auth) for role-based access control — ADMIN role required for write operations
- **DB migration**: New `categoria` table
- **Seed**: Initial category data added to seed script
