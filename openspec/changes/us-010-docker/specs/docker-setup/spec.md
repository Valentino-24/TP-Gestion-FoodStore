## ADDED Requirements

### Requirement: Docker Compose environment
The system SHALL provide a `docker-compose.yml` that starts all services with a single command.

#### Scenario: Start all services
- **WHEN** the developer runs `docker compose up --build`
- **THEN** PostgreSQL 16, the backend API (port 8000), and the frontend (port 5173) start and are accessible

#### Scenario: Backend hot-reload
- **WHEN** the developer modifies a Python file in `backend/`
- **THEN** the backend service automatically reloads (via uvicorn --reload)

#### Scenario: Frontend hot-reload
- **WHEN** the developer modifies a file in `frontend/src/`
- **THEN** the frontend service automatically reloads (via Vite dev server)

### Requirement: Automated migrations and seed data
The system SHALL run Alembic migrations and seed data automatically when the backend starts.

#### Scenario: Migrations run on startup
- **WHEN** the backend container starts
- **THEN** Alembic migrations are executed before the application starts serving requests

#### Scenario: Seed data on empty database
- **WHEN** the backend starts and the database is empty
- **THEN** the seed data script populates the database with initial categories, products, and admin user

### Requirement: Database persistence
The system SHALL persist PostgreSQL data across container restarts.

#### Scenario: Data survives restart
- **WHEN** the developer runs `docker compose down` and then `docker compose up`
- **THEN** all previously stored data (users, products, orders) is still available

### Requirement: Isolated environment
The system SHALL not interfere with existing local development setups.

#### Scenario: Port conflict
- **WHEN** the developer already has PostgreSQL running on port 5432
- **THEN** the docker-compose.yml SHALL allow changing the host port via environment variable or documented configuration
