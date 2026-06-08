## ADDED Requirements

### Requirement: Admin dashboard with charts
The system SHALL provide an admin dashboard at `/admin` with interactive charts using recharts, showing business metrics and trends.

#### Scenario: Dashboard shows revenue chart
- **WHEN** an ADMIN user navigates to /admin
- **THEN** the dashboard displays a line chart of daily revenue for the last 7 days

#### Scenario: Dashboard shows order status distribution
- **WHEN** an ADMIN user navigates to /admin
- **THEN** the dashboard displays a pie chart showing order count by estado (PENDIENTE, CONFIRMADO, EN_PREPARACION, EN_CAMINO, ENTREGADO, CANCELADO)

#### Scenario: Dashboard shows top products
- **WHEN** an ADMIN user navigates to /admin
- **THEN** the dashboard displays a bar chart of the top 5 most ordered products

#### Scenario: Dashboard data is fetched via TanStack Query
- **WHEN** an ADMIN user navigates to /admin
- **THEN** chart data is fetched via useQuery with appropriate stale time for dashboard metrics
