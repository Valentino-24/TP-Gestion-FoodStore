## Prerequisites

- [x] us-002-categorias is complete (model, migration, CRUD endpoints, seed data)
- [x] Openspec CLI is available
- [x] Alembic installed and configured in `backend/`
- [x] Auth module (us-001) provides `require_role(["ADMIN"])` dependency

---

## Task Groups

### 1. Producto Model

- [x] **1.1** Create `backend/app/models/producto.py` with Producto model:
  - id: Integer (PK, auto-increment)
  - nombre: String(200) (NOT NULL, indexed)
  - descripcion: Text (nullable)
  - precio: Float (NOT NULL)
  - categoria_id: Integer (FK → categoria.id, NOT NULL, indexed)
  - imagen_url: String(500) (nullable)
  - activo: Boolean (default True, NOT NULL)
  - creado_en: DateTime (server_default=func.now(), NOT NULL)
  - actualizado_en: DateTime (server_default=func.now(), onupdate=func.now(), NOT NULL)
- [x] **1.2** Register Producto in `backend/app/models/__init__.py` (import Producto, add to `__all__`)

### 2. Alembic Migration

- [x] **2.1** Generate migration: `alembic revision --autogenerate -m "add producto table"`
  - Verified migration creates `producto` table with all columns
  - Verified FK constraint `categoria_id → categoria.id` is generated correctly
  - Verified index on `nombre` and `categoria_id`
- [x] **2.2** Review generated migration file and rename to descriptive name
- [x] **2.3** Apply migration: `alembic upgrade head`
- [x] **2.4** Verify table exists and FK constraint is in place

### 3. Pydantic Schemas

- [x] **3.1** Create `backend/app/productos/schemas.py` with:
  - `ProductoCreate` (nombre: str, descripcion: Optional[str], precio: float ≥ 0, categoria_id: int, imagen_url: Optional[str])
  - `ProductoUpdate` (all fields optional, partial update)
  - `ProductoResponse` (all model fields, includes id, activo, creado_en, actualizado_en)

### 4. Repository

- [x] **4.1** Create `backend/app/productos/repository.py` with `ProductoRepository(BaseRepository[Producto])`:
  - `get_active(skip: int, limit: int, categoria_id: Optional[int] = None)` → paginated list of active products, ordered by nombre, optional filter by categoria_id
  - `get_by_id(producto_id: int)` → single product by id (includes inactive)
  - `count_active(categoria_id: Optional[int] = None)` → total count for pagination metadata

### 5. Service

- [x] **5.1** Create `backend/app/productos/service.py` with `ProductoService`:
  - `create(data: ProductoCreate)` → validates categoria_id exists, creates Producto, returns ProductoResponse
  - `get_all(page: int, size: int, categoria_id: Optional[int])` → returns paginated response with items, total, page, size
  - `get_by_id(producto_id: int)` → returns ProductoResponse or raises 404
  - `update(producto_id: int, data: ProductoUpdate)` → validates categoria_id if provided, updates fields, returns updated ProductoResponse or raises 404
  - `delete(producto_id: int)` → soft-delete (set activo=False), returns None or raises 404

### 6. Router

- [x] **6.1** Create `backend/app/productos/router.py` with FastAPI router at prefix `/productos`:
  - `GET /` → list products (paginated, optional categoria_id filter). Dependency: `Depends(require_auth)`.
  - `GET /{id}` → get single product. Dependency: `Depends(require_auth)`.
  - `POST /` → create product. Dependency: `Depends(require_auth)`, `admin=Depends(require_role(["ADMIN"]))`.
  - `PUT /{id}` → update product. Dependency: `admin=Depends(require_role(["ADMIN"]))`.
  - `DELETE /{id}` → soft-delete product. Dependency: `admin=Depends(require_role(["ADMIN"]))`.
- [x] **6.2** Register `productos_router` in `backend/app/main.py` with `include_router(productos_router, prefix="/api/v1")`

### 7. Seed Data

- [x] **7.1** Add seed products to `backend/app/db/seed.py`:
  - Define `PRODUCTOS` list with sample products referencing existing seed categories:
    - Bebidas: Coca-Cola ($2.50), Agua ($1.00), Jugo de Naranja ($3.00)
    - Comidas: Hamburguesa ($8.50), Pizza ($12.00), Ensalada ($7.50)
    - Snacks: Papas Fritas ($3.50), Nachos ($4.00), Barrita de cereal ($1.50)
    - Postres: Helado ($4.50), Flan ($3.00), Brownie ($2.50)
    - Otros: Salsa de tomate ($1.00), Mayonesa ($1.00), Aderezo ($1.50)
  - Add `seed_productos()` function
  - Call `seed_productos()` from main seed function after `seed_categorias()`

### 8. Verification

- [ ] **8.1** Verify POST /api/v1/productos (admin) → 201
- [ ] **8.2** Verify POST /api/v1/productos (non-admin) → 403
- [ ] **8.3** Verify POST /api/v1/productos with invalid categoria_id → 404
- [ ] **8.4** Verify GET /api/v1/productos (authenticated) → 200 with paginated list
- [ ] **8.5** Verify GET /api/v1/productos?categoria_id=1 → 200, filtered
- [ ] **8.6** Verify GET /api/v1/productos (unauthenticated) → 401
- [ ] **8.7** Verify GET /api/v1/productos/{id} → 200
- [ ] **8.8** Verify GET /api/v1/productos/{id} (non-existent) → 404
- [ ] **8.9** Verify PUT /api/v1/productos/{id} → 200
- [ ] **8.10** Verify DELETE /api/v1/productos/{id} → 204 + soft-delete confirmed
- [ ] **8.11** Verify seed products exist after seed
- [ ] **8.12** Verify pagination: GET /api/v1/productos?page=1&size=3 returns correct count

---

## Notes

- **Router Depends pattern**: Use `admin=Depends(require_role(["ADMIN"]))` (bare Depends, no type annotation as `CurrentUser`). See us-002-categorias archive for the working pattern.
- **Alembic env.py**: Ensure `migrations/env.py` has `from app.models import *` so autogenerate sees all models (including Producto).
- **Pagination**: Use `page` (1-indexed) and `size` query params. Response format: `{ "items": [...], "total": int, "page": int, "size": int }`.
- **Categoria FK**: Validate categoria_id exists before creating/updating a product. Return 404 with "Categoria no encontrada" if not found.
- **Precio**: Validate >= 0 in Pydantic schema. Use `Field(ge=0)`.
