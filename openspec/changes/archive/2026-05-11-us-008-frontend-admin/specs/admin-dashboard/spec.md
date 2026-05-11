## ADDED Requirements

### Requirement: Dashboard stats endpoint
The system SHALL provide a `GET /api/v1/admin/stats` endpoint that returns aggregated metrics for the admin dashboard.

#### Scenario: Stats return correct metrics
- **WHEN** an ADMIN user sends GET /api/v1/admin/stats
- **THEN** the system returns HTTP 200 with: today_pedidos_count, today_ingresos, total_productos_activos, total_clientes_activos

### Requirement: Dashboard UI
The system SHALL display dashboard cards with key metrics at `/admin`.

#### Scenario: Dashboard loads stats
- **WHEN** an ADMIN user navigates to /admin
- **THEN** the page displays 4 cards: Pedidos hoy, Ingresos hoy, Productos activos, Clientes activos

#### Scenario: Stats loading state
- **WHEN** stats are loading
- **THEN** each card shows a skeleton/animated placeholder

#### Scenario: Stats error state
- **WHEN** the stats endpoint fails
- **THEN** the page shows an error message with a retry button
