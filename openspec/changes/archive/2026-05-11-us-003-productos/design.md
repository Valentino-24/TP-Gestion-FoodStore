## Context

The FoodStore backend has auth (us-001) and categorias (us-002) complete. The auth module provides JWT-based authentication and RBAC with ADMIN, STOCK, PEDIDOS, CLIENT roles. The categorias module provides a flat category structure with soft-delete via `activo` flag. Products are the next logical domain entity — they depend on categorias via foreign key and will later be referenced by orders, inventory, etc.

Existing app structure uses SQLModel + SQLAlchemy async, `BaseRepository[T]` pattern for DB operations, Pydantic schemas for validation, and service/router layers for all CRUD modules.

## Goals / Non-Goals

**Goals:**
- Producto model with id, nombre, descripcion, precio, categoria_id (FK to categoria), imagen_url, activo, creado_en, actualizado_en
- Full CRUD REST API at `/api/v1/productos`
- Admin-only write (POST, PUT, DELETE); authenticated users read (GET)
- Soft delete via `activo = false` flag (same pattern as categorias)
- Filter products by categoria_id via query parameter
- Pagination for product listing (page/size)
- Alembic migration for the producto table with FK constraint
- Product seed data

**Non-Goals:**
- Image file upload (imagen_url stored as string only — file upload is a separate change)
- Stock/inventory tracking (future module)
- Discount/pricing rules (future)
- Search/full-text search (basic filtering only)
- Sorting options (ordered by nombre for now)
- Bulk operations (create/update/delete one at a time)
- Category validation beyond FK existence (categorias module handles its own validation)

## Architecture

### Data Model

```
producto
├── id: Integer (PK, auto-increment)
├── nombre: String(200) (NOT NULL, indexed)
├── descripcion: Text (nullable)
├── precio: Float (NOT NULL, >= 0)
├── categoria_id: Integer (FK → categoria.id, NOT NULL, indexed)
├── imagen_url: String(500) (nullable)
├── activo: Boolean (default true, NOT NULL)
├── creado_en: DateTime (server default now)
└── actualizado_en: DateTime (server default now, on update)
```

### Module Structure

```
backend/app/productos/
├── __init__.py
├── schemas.py       → Pydantic models: ProductoCreate, ProductoUpdate, ProductoResponse, ProductoListResponse
├── repository.py    → ProductoRepository extends BaseRepository[Producto]
├── service.py       → ProductoService with business logic
└── router.py        → FastAPI router at /api/v1/productos
```

### API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/v1/productos | Authenticated | List active products (paginated, optional categoria_id filter) |
| GET | /api/v1/productos/{id} | Authenticated | Get single product by ID |
| POST | /api/v1/productos | ADMIN | Create a new product |
| PUT | /api/v1/productos/{id} | ADMIN | Update product fields |
| DELETE | /api/v1/productos/{id} | ADMIN | Soft-delete product (activo = false) |

### Pagination

Use existing `core/pagination.py` pattern (PageParams, PagedResponse). Default page=1, size=20. Returns total count and next/prev page metadata.

## Decisions

| Decision | Choice | Rationale | Alternatives |
|----------|--------|-----------|-------------|
| Soft delete | `activo: bool` flag | Consistent with categorias. Products will be referenced by orders — hard delete would orphan references. | Hard delete |
| Price type | `float` with Pydantic validator (>= 0, 2 decimals) | Simple, sufficient for food store pricing. FastAPI serializes floats natively. | Decimal (overkill for this scope) |
| FK constraint | `categoria_id → categoria.id` with RESTRICT | Prevents assigning products to non-existent categories. RESTRICT (no action) preserves category soft-delete behavior. | CASCADE, SET NULL |
| Pagination | Page/size via core/pagination.py | Products can be many — pagination needed from start. Reuses existing pattern. | No pagination (categorias approach) |
| Category filter | Optional query param `categoria_id` | Most common product query pattern. Filtered at DB level via WHERE clause. | Client-side filter |
| Repository | `ProductoRepository` extends `BaseRepository[Producto]` with custom methods | Need filtered queries (by categoria_id, active). Can reuse `get_active()` from categorias pattern. | Inline in service |
| Admin write | `require_role(["ADMIN"])` dependency | Reuses existing RBAC. Same pattern as categorias. | Custom permission |
| Unique constraint | No unique constraint on nombre | Products can share names (e.g., "Coca-Cola" in Bebidas and "Coca-Cola" in Snacks). A product is identified by id only. | Unique nombre |
| Imagen URL | String(500), nullable | URL stored as text. File upload and serving is a separate change. | BLOB storage |

## Risks / Trade-offs

- [Risk] Deleting a category with active products → Mitigated by precio validation (GET /productos filters by active categoria if needed). FK is RESTRICT — trying to hard-delete a category with products would fail at DB level. Since categorias uses soft-delete, this is fine.
- [Risk] Product list grows large → Mitigated by pagination from the start. Default page size 20 is reasonable.
- [Trade-off] Float for price → Simpler implementation. Accepts minor floating-point precision issues (negligible for food store pricing where prices are typically .00/.50/.90).
- [Risk] Missing category_id validation → Mitigated by DB FK constraint. API returns 404 if categoria_id does not reference an existing category.
