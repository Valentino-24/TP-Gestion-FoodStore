# RBAC

Specification for the role-based access control system.

## MODIFIED Requirements

### Requirement: Fixed role definitions
The system SHALL use exactly five predefined roles with stable IDs: ADMIN (1), STOCK (2), PEDIDOS (3), CLIENT (4), COCINA (5). These roles SHALL be seeded in the database and SHALL NOT be modifiable through the application.

#### Scenario: Role IDs are stable
- **WHEN** the system checks for ADMIN role
- **THEN** it references the role with id=1, not by string comparison alone

#### Scenario: New roles cannot be created via app
- **WHEN** an attempt is made to create a new role via the application
- **THEN** the system rejects the operation (roles are seed-only data)

#### Scenario: COCINA role exists
- **WHEN** the database seed runs
- **THEN** the system creates or verifies the COCINA role with codigo='COCINA', nombre='Cocinero', id=5

## ADDED Requirements

### Requirement: COCINA access to KDS endpoints
The system SHALL protect KDS endpoints with `require_role(["COCINA", "PEDIDOS", "ADMIN"])`.

#### Scenario: COCINA accesses KDS
- **WHEN** a user with COCINA role sends GET /api/v1/cocina/pedidos
- **THEN** the request is authorized

#### Scenario: CLIENT cannot access KDS
- **WHEN** a user with only CLIENT role attempts to access /api/v1/cocina/pedidos
- **THEN** the system returns HTTP 403 Forbidden

### Requirement: Per-role transition authorization in FSM
The system SHALL enforce that each state transition is only executable by authorized roles, as defined by the role-transitions map. This validation SHALL happen in the service layer (not only at endpoint level) to prevent a role from executing transitions beyond its authority.

#### Scenario: COCINA authorized kitchen transitions
- **WHEN** a user with COCINA role attempts CONFIRMADO → EN_PREP or EN_PREP → EN_CAMINO
- **THEN** the transition is authorized by the service layer

#### Scenario: COCINA unauthorized dispatch transition
- **WHEN** a user with COCINA role attempts EN_CAMINO → ENTREGADO
- **THEN** the service layer returns HTTP 403 before executing the transition
