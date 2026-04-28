## ADDED Requirements

### Requirement: Seed data for catalog tables
The application SHALL provide a seed script that populates initial reference data.

#### Scenario: Roles table seeded
- **WHEN** seed script runs
- **THEN** creates 4 roles: ADMIN(1), STOCK(2), PEDIDOS(3), CLIENT(4)

#### Scenario: EstadoPedido table seeded
- **WHEN** seed script runs
- **THEN** creates 6 estados: PENDIENTE(1), CONFIRMADO(2), EN_PREPARACION(3), EN_CAMINO(4), ENTREGADO(5), CANCELADO(6)

#### Scenario: FormaPago table seeded
- **WHEN** seed script runs
- **THEN** creates: Tarjeta de credito (activa), Tarjeta de debito (activa)

#### Scenario: Seed is idempotent
- **WHEN** seed script runs multiple times
- **THEN** does not duplicate existing records