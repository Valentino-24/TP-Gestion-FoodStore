## Why

El proyecto tiene 10 cambios implementados (backend completo con 9 módulos + frontend completo con catálogo, carrito, checkout, admin y perfil) pero cero tests automatizados. Cada verificación se hace manualmente contra la API o navegando el frontend. No hay red de seguridad para refactors, cambios de dependencias, o nuevas features. Sin tests, cada cambio futuro tiene riesgo de regresión no detectada.

## What Changes

- **Backend testing**: Infraestructura completa de tests con pytest + pytest-asyncio + httpx
  - Tests unitarios para servicios y repositorios de cada módulo
  - Tests de integración para todos los endpoints REST
  - Base de datos de test separada (PostgreSQL o SQLite in-memory)
  - Fixtures reutilizables para auth, datos seed, y cliente HTTP
  - Cobertura mínima: módulos auth, categorias, productos, clientes, pedidos, pagos, direcciones

- **Frontend testing**: Infraestructura con Vitest + Testing Library
  - Tests de componentes para páginas y componentes clave
  - Tests de stores (Zustand)
  - Tests del apiClient (axios interceptors)
  - Cobertura mínima: auth store, cart store, ProductCard, LoginPage, componentes compartidos

## Capabilities

### New Capabilities

- `backend-testing`: Test suite automatizado para backend FastAPI — tests unitarios de servicios/repositorios + tests de integración de endpoints con base de datos de test y fixtures reutilizables
- `frontend-testing`: Test suite automatizado para frontend React — tests de componentes con Vitest + Testing Library, tests de stores Zustand, y tests del API client

### Modified Capabilities

<!-- No existing specs change — testing es infraestructura nueva, no modifica requerimientos de funcionalidad existente -->

## Impact

- **Nuevos archivos**: `backend/tests/` (estructura completa), `frontend/src/**/*.test.tsx`, configs de pytest y vitest
- **Nuevas dependencias**: pytest, pytest-asyncio, httpx, pytest-cov (backend); vitest, @testing-library/react, jsdom (frontend)
- **Base de datos de test**: Se usará una base PostgreSQL separada (o SQLite in-memory) para no contaminar datos de desarrollo
- **No rompe flujo existente**: Los tests son新增, no modifican código de producción
- **CI-ready**: La estructura de tests está diseñada para integrarse con CI/CD en el futuro
