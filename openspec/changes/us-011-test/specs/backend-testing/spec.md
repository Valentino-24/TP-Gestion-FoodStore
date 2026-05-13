# Backend Testing

Specification for automated backend testing infrastructure — unit tests for services/repositories and integration tests for API endpoints.

## ADDED Requirements

### Requirement: Backend test infrastructure
The system SHALL provide a pytest-based test suite with async support (pytest-asyncio), HTTP client (httpx), coverage reporting (pytest-cov), and a dedicated test database.

#### Scenario: pytest configuration exists
- **WHEN** the developer runs `pytest` in the `backend/` directory
- **THEN** pytest discovers and runs all tests using configured async support

#### Scenario: Tests use separate database
- **WHEN** tests are executed
- **THEN** they connect to `foodstore_test` database, not the development database

#### Scenario: Tests are isolated
- **WHEN** a test finishes
- **THEN** its changes are rolled back or cleaned up, so subsequent tests start with a clean state

#### Scenario: Coverage report is generated
- **WHEN** the developer runs `pytest --cov=app`
- **THEN** a coverage report SHALL be generated showing percentage per module

### Requirement: Unit tests for repositories
The system SHALL test each module's repository with focus on CRUD operations and custom query methods.

#### Scenario: Create entity via repository
- **WHEN** a repository's create method is called with valid data
- **THEN** the entity is saved to the database and returned with a generated ID

#### Scenario: Get entity by ID
- **WHEN** a repository's get_by_id method is called with an existing ID
- **THEN** the correct entity is returned

#### Scenario: Get entity by ID (not found)
- **WHEN** a repository's get_by_id method is called with a non-existent ID
- **THEN** None is returned

#### Scenario: Paginated list
- **WHEN** a repository's get_all method is called with skip/limit
- **THEN** the correct subset of entities is returned with proper pagination

#### Scenario: Update entity
- **WHEN** a repository's update method is called on a modified entity
- **THEN** the changes are persisted to the database

#### Scenario: Delete entity (soft or hard)
- **WHEN** a repository's delete method is called
- **THEN** the entity is removed or marked as inactive in the database

#### Scenario: Custom query methods
- **WHEN** a repository's custom method (e.g. get_by_email, count_active) is called
- **THEN** the method returns the correct result set

### Requirement: Unit tests for services
The system SHALL test each module's service layer to validate business logic, validation rules, error handling, and auth enforcement.

#### Scenario: Create with valid data
- **WHEN** the service's create method is called with valid input
- **THEN** the entity is created and the correct response schema is returned

#### Scenario: Create with invalid data
- **WHEN** the service's create method is called with invalid input (e.g. duplicate email, non-existent FK)
- **THEN** the service raises the appropriate HTTPException with correct status code and message

#### Scenario: Get by ID (found)
- **WHEN** the service's get_by_id is called with an existing ID
- **THEN** the entity response is returned

#### Scenario: Get by ID (not found)
- **WHEN** the service's get_by_id is called with a non-existent ID
- **THEN** HTTPException 404 is raised

#### Scenario: Update with valid data
- **WHEN** the service's update method is called with a valid ID and data
- **THEN** the entity is updated and the updated response is returned

#### Scenario: Delete (soft-delete)
- **WHEN** the service's delete method is called
- **THEN** the entity's active flag is set to False (or equivalent soft-delete)

#### Scenario: Authorization enforcement in service
- **WHEN** a service method requires admin privileges
- **THEN** only users with the ADMIN role can execute the operation

### Requirement: Integration tests for API endpoints
The system SHALL test all REST API endpoints via HTTP using httpx.AsyncClient with ASGI transport, covering happy paths, error cases, and auth enforcement.

#### Scenario: Health check endpoint
- **WHEN** a GET request is sent to /health
- **THEN** the response returns 200 with `{"status": "healthy"}`

#### Scenario: Auth registration (success)
- **WHEN** a POST request is sent to /api/v1/auth/register with valid data
- **THEN** the response returns 201 with access_token and refresh_token

#### Scenario: Auth registration (duplicate email)
- **WHEN** a POST request is sent to /api/v1/auth/register with an existing email
- **THEN** the response returns 409 with error message

#### Scenario: Auth registration (weak password)
- **WHEN** a POST request is sent to /api/v1/auth/register with a short password
- **THEN** the response returns 422 with validation error

#### Scenario: Auth login (success)
- **WHEN** a POST request is sent to /api/v1/auth/login with valid credentials
- **THEN** the response returns 200 with JWT access token and refresh token

#### Scenario: Auth login (invalid credentials)
- **WHEN** a POST request is sent to /api/v1/auth/login with wrong password
- **THEN** the response returns 401 with "Credenciales invalidas"

#### Scenario: Auth /me (authenticated)
- **WHEN** a GET request is sent to /api/v1/auth/me with a valid Bearer token
- **THEN** the response returns 200 with user profile data

#### Scenario: Auth /me (unauthenticated)
- **WHEN** a GET request is sent to /api/v1/auth/me without a token
- **THEN** the response returns 401

#### Scenario: Token refresh (valid)
- **WHEN** a POST request is sent to /api/v1/auth/refresh with a valid refresh token
- **THEN** the response returns 200 with new token pair

#### Scenario: Token refresh (replay attack)
- **WHEN** the same refresh token is used twice (replay)
- **THEN** the response returns 401 and ALL user tokens are revoked

#### Scenario: Logout
- **WHEN** a POST request is sent to /api/v1/auth/logout with a valid refresh token
- **THEN** the response returns 204 and the token is revoked

#### Scenario: CRUD endpoints (authenticated)
- **WHEN** an authenticated user sends GET/POST/PUT/DELETE requests to CRUD endpoints
- **THEN** the correct HTTP status codes and response bodies are returned

#### Scenario: CRUD endpoints (unauthenticated)
- **WHEN** an unauthenticated user sends requests to protected endpoints
- **THEN** the response returns 401

#### Scenario: Admin endpoints (non-admin)
- **WHEN** a non-admin user sends requests to admin-only endpoints
- **THEN** the response returns 403

#### Scenario: Pagination works correctly
- **WHEN** a paginated GET endpoint is called with page and size parameters
- **THEN** the response includes items, total count, page number, and page size

#### Scenario: Not found returns 404
- **WHEN** a GET/PUT/DELETE request is sent with a non-existent ID
- **THEN** the response returns 404 with an appropriate error message

#### Scenario: Rate limiting on login
- **WHEN** the login endpoint receives too many failed attempts from the same IP
- **THEN** the response returns 429

### Requirement: Fixtures for all modules
The system SHALL provide reusable pytest fixtures for database session, HTTP client, auth headers, and module-specific test data.

#### Scenario: db_session fixture
- **WHEN** a test requests the db_session fixture
- **THEN** it receives an AsyncSession connected to the test database

#### Scenario: async_client fixture
- **WHEN** a test requests the async_client fixture
- **THEN** it receives an httpx.AsyncClient configured with ASGI transport for the FastAPI app

#### Scenario: auth_headers fixture
- **WHEN** a test requests the auth_headers fixture
- **THEN** it receives valid Bearer token headers for an authenticated user

#### Scenario: admin_headers fixture
- **WHEN** a test requests the admin_headers fixture
- **THEN** it receives valid Bearer token headers for an ADMIN user

#### Scenario: Module-specific fixtures
- **WHEN** a test requests a module fixture (e.g. sample_product, sample_category)
- **THEN** it receives pre-created entity data in the test database
