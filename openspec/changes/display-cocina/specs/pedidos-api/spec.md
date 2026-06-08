# Pedidos API

Specification for the backend orders module with FSM state management.

## MODIFIED Requirements

### Requirement: Pedido model with FSM
The system SHALL provide a Pedido model with fields: id, usuario_id (FK), estado (FK to estado_pedido), total, direccion_id (nullable), forma_pago_id (nullable), creado_en, actualizado_en. The system SHALL enforce a finite state machine for estado transitions. The system SHALL additionally enforce per-role transition permissions: users with the COCINA role SHALL only be permitted to execute CONFIRMADO → EN_PREP and EN_PREP → EN_CAMINO transitions; PEDIDOS and ADMIN SHALL have broader permissions as defined in the role-transitions map.

#### Scenario: Create pedido
- **WHEN** an authenticated user submits a POST to /api/v1/pedidos with items, direccion_id, and forma_pago_id
- **THEN** the system creates a Pedido with estado="PENDIENTE", calculates total from items, and returns HTTP 201 with the pedido data

#### Scenario: Valid state transitions
- **WHEN** an ADMIN transitions a pedido from PENDIENTE to CONFIRMADO
- **THEN** the system updates the estado and returns HTTP 200

#### Scenario: Invalid state transition
- **WHEN** an ADMIN attempts to transition a pedido from PENDIENTE directly to ENTREGADO
- **THEN** the system returns HTTP 400 with an error indicating invalid transition

#### Scenario: Cancel pedido
- **WHEN** an ADMIN cancels a pedido in PENDIENTE or CONFIRMADO state
- **THEN** the system sets estado to CANCELADO

#### Scenario: Cannot cancel after preparation
- **WHEN** an ADMIN attempts to cancel a pedido in EN_PREPARACION or later state
- **THEN** the system returns HTTP 400

#### Scenario: COCINA transition from CONFIRMADO to EN_PREP
- **WHEN** a user with COCINA role sends PATCH /api/v1/pedidos/{id}/estado with nuevo_estado=EN_PREP
- **THEN** the system transitions the pedido from CONFIRMADO to EN_PREP and returns HTTP 200

#### Scenario: COCINA transition from EN_PREP to EN_CAMINO
- **WHEN** a user with COCINA role sends PATCH /api/v1/pedidos/{id}/estado with nuevo_estado=EN_CAMINO
- **THEN** the system transitions the pedido from EN_PREP to EN_CAMINO and returns HTTP 200

#### Scenario: COCINA forbidden transition
- **WHEN** a user with COCINA role attempts to transition a pedido from EN_CAMINO to ENTREGADO
- **THEN** the system returns HTTP 403 Forbidden (role not authorized for this transition)

### Requirement: List user pedidos
The system SHALL allow authenticated users to list their own pedidos, and ADMIN users to list all pedidos, with pagination. Unchanged from previous version.

#### Scenario: User lists own pedidos
- **WHEN** an authenticated CLIENT sends GET /api/v1/pedidos
- **THEN** the system returns HTTP 200 with paginated pedidos belonging to that user

#### Scenario: ADMIN lists all pedidos
- **WHEN** an ADMIN sends GET /api/v1/pedidos
- **THEN** the system returns HTTP 200 with all pedidos

### Requirement: Get pedido detail
The system SHALL allow users to view their own pedido detail, and ADMIN to view any pedido. Unchanged from previous version.

#### Scenario: Get pedido with items
- **WHEN** an authenticated user sends GET /api/v1/pedidos/{id}
- **THEN** the system returns HTTP 200 with pedido data including items, estado history, and payment info

## ADDED Requirements

### Requirement: COCINA can access estado endpoint
The system SHALL expand PATCH /api/v1/pedidos/{id}/estado to accept users with COCINA role (in addition to ADMIN). The endpoint-level dependency SHALL use `require_role(["COCINA", "PEDIDOS", "ADMIN"])`.

#### Scenario: COCINA can access the endpoint
- **WHEN** a user with COCINA role sends PATCH /api/v1/pedidos/{id}/estado
- **THEN** the endpoint accepts the request (transition validation happens in the service layer)
