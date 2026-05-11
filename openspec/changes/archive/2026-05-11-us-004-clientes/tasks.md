## 1. Modelo y Migración

- [x] 1.1 Crear backend/app/models/cliente.py con modelo Cliente: id, nombre, apellido, email (único), telefono, direccion, activo, creado_en, actualizado_en
- [x] 1.2 Registrar Cliente en backend/app/models/__init__.py
- [x] 1.3 Crear migración Alembic para tabla clientes
- [x] 1.4 Aplicar migración y verificar tabla y unicidad de email

## 2. Schemas

- [x] 2.1 Crear backend/app/clientes/schemas.py con ClienteCreate, ClienteUpdate, ClienteResponse

## 3. Repository

- [x] 3.1 Crear backend/app/clientes/repository.py: ClienteRepository con métodos para CRUD, filtrado por activo y email

## 4. Service

- [x] 4.1 Crear backend/app/clientes/service.py: ClienteService con validación de email único y lógica de negocio

## 5. Router y Endpoints

- [x] 5.1 Crear backend/app/clientes/router.py con rutas REST (/api/v1/clientes): CRUD, seguridad por rol (ADMIN full, CLIENT sólo el propio)
- [x] 5.2 Registrar clientes_router en backend/app/main.py (prefix="/api/v1")

## 6. Seed Data

- [x] 6.1 Agregar clientes de ejemplo en backend/app/db/seed.py y función seed_clientes()

## 7. Verificación

- [x] 7.1 Administrador crea cliente (POST) → 201
- [x] 7.2 No admin intenta crear/modificar → 403
- [x] 7.3 Email duplicado → 422
- [x] 7.4 Consulta paginada (GET) → 200
- [x] 7.5 Cliente sólo accede al propio → 403 si accede a otro
- [x] 7.6 Modificación (PUT) por admin → 200
- [x] 7.7 Soft delete (DELETE) → 204 + no aparece en GET/lista
