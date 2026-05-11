# Pedidos API

Specification for the backend orders module with FSM state management.

## Requirements

### Requirement: Pedido model with FSM
The system SHALL provide a Pedido model with fields: id, usuario_id (FK), estado (FK to estado_pedido), total, direccion_id (nullable), forma_pago_id (nullable), creado_en, actualizado_en. The system SHALL enforce a finite state machine for estado transitions.

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

### Requirement: List user pedidos
The system SHALL allow authenticated users to list their own pedidos, and ADMIN users to list all pedidos, with pagination.

#### Scenario: User lists own pedidos
- **WHEN** an authenticated CLIENT sends GET /api/v1/pedidos
- **THEN** the system returns HTTP 200 with paginated pedidos belonging to that user

#### Scenario: ADMIN lists all pedidos
- **WHEN** an ADMIN sends GET /api/v1/pedidos
- **THEN** the system returns HTTP 200 with all pedidos

### Requirement: Get pedido detail
The system SHALL allow users to view their own pedido detail, and ADMIN to view any pedido.

#### Scenario: Get pedido with items
- **WHEN** an authenticated user sends GET /api/v1/pedidos/{id}
- **THEN** the system returns HTTP 200 with pedido data including items, estado history, and payment info
