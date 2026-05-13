## Context

El proyecto FoodStore tiene 9 módulos backend (auth, categorias, productos, clientes, pedidos, pagos, direcciones, refreshtokens, admin) y 10+ páginas frontend, todo funcionando. Sin embargo, no existe ni un solo test automatizado. Las verificaciones se hacen manualmente contra la API con curl o navegando el frontend.

El backend usa:
- FastAPI + SQLModel + asyncpg (PostgreSQL asíncrono)
- Unit of Work pattern con AsyncSession de SQLAlchemy
- BaseRepository genérico con CRUD común
- Servicios con lógica de negocio + validaciones
- Dependencias FastAPI para auth (get_current_user, require_role)

El frontend usa:
- React + TypeScript + Vite
- Zustand para stores (authStore, cartStore)
- Axios con interceptors (apiClient)
- React Router DOM para navegación

## Goals / Non-Goals

**Goals:**
- Configurar pytest con pytest-asyncio y httpx para tests backend
- Tests unitarios de servicios y repositorios para cada módulo backend
- Tests de integración de endpoints REST vía HTTP real (httpx.AsyncClient)
- Base de datos de test separada (PostgreSQL con DB name `foodstore_test`)
- Fixtures reutilizables: async client autenticado, session de DB, seed data
- Cobertura de escenarios críticos: auth flows, CRUD operations, validaciones, error handling, RBAC
- Configurar Vitest + Testing Library para frontend
- Tests de stores Zustand (authStore, cartStore)
- Tests de componentes clave (ProductCard, LoginPage, Navbar)
- Tests del apiClient (interceptor de refresh, manejo de 401)
- Reporte de cobertura (pytest-cov backend, istanbul frontend)

**Non-Goals:**
- Tests end-to-end con Playwright (se deja para un cambio futuro)
- Cobertura del 100% (se priorizan caminos críticos)
- Tests de componentes visuales complejos (pantalla completa de checkout)
- Performance / load testing
- Tests de migraciones Alembic

## Decisions

| Decisión | Opción elegida | Alternativas | Razón |
|----------|---------------|--------------|-------|
| DB de test | PostgreSQL `foodstore_test` | SQLite in-memory | SQLite no soporta funciones PG nativas como `func.now()` y tsvector; usar misma BD que producción evita falsos positivos |
| Aislamiento de tests | Por módulo, con truncate entre tests | Por test (rollback) | Truncate es más simple con SQLModel; rollback requiere manejo cuidadoso de transacciones anidadas |
| Cliente HTTP para tests | httpx.AsyncClient con `asgi_transport` | requests | httpx es nativamente async, compatible con FastAPI TestClient, y permite testear sin servidor real |
| Estrategia de fixtures | `conftest.py` global + por módulo | Fixtures planas | Separación clara: fixtures globales (DB, client, auth headers) + específicas de módulo (producto test data) |
| Auth en tests | Fixture `auth_headers` que obtiene token vía login real | Token mockeado | Probar el flujo completo incluyendo JWT + refresh es más valioso que mockear |
| Frontend framework de tests | Vitest + jsdom | Jest + jsdom | Vitest ya es parte del stack (Vite), configuración mínima, nativo ESM y TypeScript |
| Store testing | Zustand vanilla (sin React) | renderHook | Las stores Zustand se testean directamente (acciones + estado), sin necesidad de wrappers React |
| Organización de tests backend | `tests/unit/` + `tests/integration/` | Mezclados | Separación clara: unit tests rápidos (sin DB), integration tests lentos (con DB) |

## Risks / Trade-offs

- **[Riesgo] Tests async + PostgreSQL**: Las sesiones async de SQLAlchemy requieren manejo cuidadoso de conexiones → Usar `pytest.mark.asyncio` con `scope="function"` para evitar conexiones compartidas
- **[Riesgo] Base de test no existe**: El dev debe crear `foodstore_test` antes de correr tests → Documentar en README y agregar script de setup automatizado en `conftest.py`
- **[Riesgo] Seed data puede interferir con tests**: Los seeds existentes (`seed_db.py`) insertan datos en tablas catálogo (roles, estados) → Crear fixture `seed_catalogo` que inserta datos mínimos necesarios
- **[Risk] Tests lentos por DB real**: PostgreSQL externa agrega latencia → Apuntar a < 5s para toda la suite, usar async para concurrencia
- **[Trade-off] httpx.AsyncClient con ASGI transport**: No testea la red real ni middlewares de servidor → Suficiente para tests de integración; cubre validaciones, serialización, auth, y lógica de endpoints
- **[Trade-off] Frontend sin e2e**: Componentes testeados de forma aislada no garantizan que el flujo completo funcione → Aceptable por ahora; e2e se agrega en cambio futuro
