## 1. Backend Test Infrastructure

- [x] 1.1 Add test dependencies to `backend/requirements.txt`: pytest, pytest-asyncio, httpx, pytest-cov
- [x] 1.2 Create `backend/pytest.ini` with async support configuration and test path
- [x] 1.3 Create `backend/tests/conftest.py` with base fixtures:
  - `db_session`: AsyncSession connected to `foodstore_test` database
  - `async_client`: httpx.AsyncClient with ASGI transport (FastAPI app)
  - `auth_headers`: Bearer token headers for authenticated user (CLIENT role)
  - `admin_headers`: Bearer token headers for admin user (ADMIN role)
  - `seed_catalogo`: Seed minimal catalog data (roles, estados)
- [x] 1.4 Create `backend/tests/__init__.py` (package marker)

## 2. Backend Repository Unit Tests

- [x] 2.1 Create `backend/tests/unit/__init__.py` and `backend/tests/unit/conftest.py` with module-specific fixtures
- [x] 2.2 Create `backend/tests/unit/test_base_repository.py` — tests for BaseRepository CRUD (create, get_by_id, get_all, update, delete, count)
- [x] 2.3 Create `backend/tests/unit/test_categoria_repository.py` — tests for CategoriaRepository custom queries
- [x] 2.4 Create `backend/tests/unit/test_producto_repository.py` — tests for ProductoRepository (get_active, count_active, filter by categoria_id)
- [x] 2.5 Create `backend/tests/unit/test_auth_repository.py` — tests for AuthRepository (get_by_email)
- [x] 2.6 Create `backend/tests/unit/test_cliente_repository.py` — tests for ClienteRepository custom queries
- [x] 2.7 Create `backend/tests/unit/test_pedido_repository.py` — tests for PedidoRepository custom queries

## 3. Backend Service Unit Tests

- [x] 3.1 Create `backend/tests/unit/test_auth_service.py`:
  - register: success, duplicate email, weak password
  - login: success, invalid credentials
  - Automatic CLIENT role assignment on register
- [x] 3.2 Create `backend/tests/unit/test_categoria_service.py`:
  - CRUD, soft-delete, 404 handling, admin-only enforcement
- [x] 3.3 Create `backend/tests/unit/test_producto_service.py`:
  - CRUD, validate categoria_id exists, soft-delete, pagination, admin-only create/update/delete
- [x] 3.4 Create `backend/tests/unit/test_cliente_service.py`:
  - CRUD, user ownership (CLIENT sees own, ADMIN sees all), 404 handling

## 4. Backend Integration Tests — Auth

- [x] 4.1 Create `backend/tests/integration/__init__.py` and `backend/tests/integration/conftest.py`
- [x] 4.2 Create `backend/tests/integration/test_auth_endpoints.py`:
  - POST /api/v1/auth/register (201 success, 409 duplicate, 422 weak password)
  - POST /api/v1/auth/login (200 success, 401 invalid credentials)
  - GET /api/v1/auth/me (200 authenticated, 401 unauthenticated)
  - POST /api/v1/auth/refresh (200 valid, 401 expired/replayed)
  - POST /api/v1/auth/logout (204 success, 204 idempotent)

## 5. Backend Integration Tests — CRUD Endpoints

- [x] 5.1 Create `backend/tests/integration/test_categoria_endpoints.py`:
  - CRUD endpoints, admin enforcement, 404 handling
- [x] 5.2 Create `backend/tests/integration/test_producto_endpoints.py`:
  - CRUD endpoints, category filter, pagination, admin enforcement (create/update/delete), 404 for invalid categoria_id
- [x] 5.3 Create `backend/tests/integration/test_cliente_endpoints.py`:
  - CRUD endpoints, CLIENT sees own record, ADMIN sees all, 404 handling

## 6. Backend Integration Tests — Orders, Payments, Addresses

- [x] 6.1 Create `backend/tests/integration/test_pedido_endpoints.py`:
  - Create order from cart, list own orders, admin lists all, state transitions
- [x] 6.2 Create `backend/tests/integration/test_pago_endpoints.py`:
  - Payment creation, MercadoPago integration (mock), payment status
- [x] 6.3 Create `backend/tests/integration/test_direccion_endpoints.py`:
  - CRUD, user ownership (CLIENT sees own, others can't access)

## 7. Frontend Test Infrastructure

- [x] 7.1 Add test dependencies to `frontend/package.json`: vitest, @testing-library/react, @testing-library/jest-dom, jsdom, @testing-library/user-event
- [x] 7.2 Create `frontend/vitest.config.ts` with jsdom environment and path aliases
- [x] 7.3 Create `frontend/src/setupTests.ts` with Testing Library matchers (jest-dom import)
- [x] 7.4 Update `frontend/package.json` scripts to include `test` and `test:run`

## 8. Frontend Store Tests (Zustand)

- [x] 8.1 Create `frontend/src/stores/__tests__/authStore.test.ts`:
  - Login updates state on success, doesn't mutate on failure
  - Registration updates state
  - Logout clears state and localStorage
  - Token refresh updates tokens
  - State restoration from localStorage on init
- [x] 8.2 Create `frontend/src/stores/__tests__/cartStore.test.ts`:
  - Add item to empty cart, add duplicate (increments), update quantity
  - Remove item, clear cart
  - Totals calculation (totalItems, totalPrice)
  - localStorage persistence and restoration

## 9. Frontend API Client Tests

- [x] 9.1 Create `frontend/src/lib/__tests__/apiClient.test.ts`:
  - Request interceptor: adds Bearer token when available, omits when absent
  - Response interceptor: refreshes on 401 and retries, redirects to /login on failed refresh
  - Token helpers: storeTokens, clearTokens, getStoredAccessToken, getStoredRefreshToken

## 10. Frontend Component Tests

- [x] 10.1 Create `frontend/src/components/__tests__/ProductCard.test.tsx`:
  - Renders product name, price, category badge
  - Handles missing image (placeholder)
- [x] 10.2 Create `frontend/src/components/__tests__/Pagination.test.tsx`:
  - Renders page controls with multiple pages
  - Disables "Anterior" on page 1, disables "Siguiente" on last page
  - Click handler fires on page change
- [x] 10.3 Create `frontend/src/pages/__tests__/LoginPage.test.tsx`:
  - Renders email/password inputs and submit button
  - Shows validation errors on empty submit
- [x] 10.4 Create `frontend/src/components/__tests__/ProtectedRoute.test.tsx`:
  - Redirects to /login when unauthenticated
  - Renders children when authenticated
- [x] 10.5 Create `frontend/src/components/__tests__/Navbar.test.tsx`:
  - Shows user name and logout when authenticated
  - Shows login link when unauthenticated

## 11. Verification

- [ ] 11.1 Run full backend test suite: `cd backend && pytest` — all tests pass
- [ ] 11.2 Run backend coverage: `cd backend && pytest --cov=app --cov-report=term` — review coverage
- [ ] 11.3 Run full frontend test suite: `cd frontend && npx vitest run` — all tests pass
- [ ] 11.4 Verify no flaky tests by running each suite twice
