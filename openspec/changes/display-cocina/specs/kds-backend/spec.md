# KDS Backend

Specification for the Kitchen Display System backend infrastructure.

## ADDED Requirements

### Requirement: COCINA role definition
The system SHALL provide a `COCINA` role (codigo='COCINA', nombre='Cocinero') in the Rol catalog table. The role SHALL be seeded idempotently (`INSERT ... ON CONFLICT DO NOTHING`). The system SHALL support assigning `COCINA` to any user via the existing `UsuarioRol` N:M relationship.

#### Scenario: COCINA role exists in seed
- **WHEN** the database seed runs
- **THEN** the `Rol` table contains a record with `codigo='COCINA'` and `nombre='Cocinero'`

#### Scenario: Multiple roles including COCINA
- **WHEN** a user is assigned both COCINA and PEDIDOS roles
- **THEN** the user can access endpoints authorized for COCINA AND endpoints authorized for PEDIDOS

### Requirement: KDS REST endpoint
The system SHALL provide `GET /api/v1/cocina/pedidos` that returns all pedidos in `CONFIRMADO` and `EN_PREP` states, ordered by ascending time of entry to the kitchen queue (oldest first). Each pedido SHALL include items with `nombre_snapshot`, `cantidad`, exclusiones from `personalizacion`, customer `notas`, and the `created_at` of the `CONFIRMADO` historial entry (kitchen entry timestamp).

#### Scenario: Initial load of KDS
- **WHEN** an authenticated user with COCINA role sends GET /api/v1/cocina/pedidos
- **THEN** the system returns HTTP 200 with a list of pedidos in CONFIRMADO and EN_PREP states, ordered by kitchen entry time ascending

#### Scenario: PENDIENTE pedidos excluded
- **WHEN** the system filters pedidos for the KDS
- **THEN** pedidos in PENDIENTE state are NEVER included (unpaid orders are not kitchen-relevant)

#### Scenario: Unauthorized access to KDS
- **WHEN** a user without COCINA/PEDIDOS/ADMIN role sends GET /api/v1/cocina/pedidos
- **THEN** the system returns HTTP 403 Forbidden

### Requirement: SSE event stream
The system SHALL provide `GET /api/v1/cocina/eventos` as a Server-Sent Events (SSE) endpoint. The endpoint SHALL authenticate via JWT token (query param or cookie) and reject unauthenticated connections with HTTP 401. The endpoint SHALL emit structured JSON events when pedido state changes occur in the kitchen phase.

#### Scenario: SSE stream connection
- **WHEN** an authenticated user with COCINA/PEDIDOS/ADMIN role connects to GET /api/v1/cocina/eventos
- **THEN** the server keeps the connection open and sends events as they occur

#### Scenario: SSE auth rejection
- **WHEN** an unauthenticated user attempts to connect to GET /api/v1/cocina/eventos
- **THEN** the server returns HTTP 401 and closes the connection

### Requirement: Kitchen events
The system SHALL emit the following events via SSE when pedido state transitions occur:

| Event | Triggered when | Effect |
|-------|---------------|--------|
| `PEDIDO_CONFIRMADO` | PENDIENTE → CONFIRMADO (payment approved) | New pedido enters kitchen queue |
| `PEDIDO_EN_PREPARACION` | CONFIRMADO → EN_PREP | Pedido moves to "in preparation" |
| `PEDIDO_EN_CAMINO` | EN_PREP → EN_CAMINO | Pedido leaves kitchen |
| `PEDIDO_CANCELADO` | Any → CANCELADO in kitchen phase | Pedido is removed from KDS |

Each event payload SHALL include the full pedido data (id, items, estado, timestamps, kitchen_entry_at) so the frontend can update without additional REST calls.

#### Scenario: New pedido confirmed while KDS is connected
- **WHEN** a payment is approved and a pedido transitions from PENDIENTE to CONFIRMADO
- **THEN** the system emits a `PEDIDO_CONFIRMADO` event to all connected SSE clients

#### Scenario: Pedido moves to preparation
- **WHEN** a cocinero transitions a pedido from CONFIRMADO to EN_PREP
- **THEN** the system emits a `PEDIDO_EN_PREPARACION` event to all connected SSE clients

#### Scenario: Pedido completed (leaves kitchen)
- **WHEN** a cocinero transitions a pedido from EN_PREP to EN_CAMINO
- **THEN** the system emits a `PEDIDO_EN_CAMINO` event and the pedido is removed from the KDS in all connected clients

#### Scenario: Pedido cancelled in kitchen phase
- **WHEN** an ADMIN cancels a pedido in CONFIRMADO or EN_PREP state
- **THEN** the system emits a `PEDIDO_CANCELADO` event to all connected SSE clients

### Requirement: Event publication in PedidoService
The system SHALL publish events from `PedidoService.update_estado()` and from the payment approval flow whenever a state transition affects the kitchen phase. Event publication SHALL happen after the database transaction commits. If no SSE clients are connected, the event SHALL be silently discarded (best-effort delivery for v1).

#### Scenario: Event published after state change
- **WHEN** PedidoService.update_estado() successfully transitions a pedido
- **THEN** the system publishes a kitchen event if the transition is relevant (enters CONFIRMADO, EN_PREP, exits kitchen via EN_CAMINO or CANCELADO)

### Requirement: Role-restricted state transitions
The system SHALL enforce per-role transition permissions in `PedidoService.update_estado()`. The `COCINA` role SHALL only be permitted to execute `CONFIRMADO → EN_PREP` and `EN_PREP → EN_CAMINO`. Any other transition attempted by COCINA SHALL return HTTP 403 even if the endpoint-level `require_role` passes.

#### Scenario: COCINA performs allowed transition
- **WHEN** a user with COCINA role requests a transition from CONFIRMADO to EN_PREP
- **THEN** the system accepts the transition and records historial with the cocinero's usuario_id

#### Scenario: COCINA attempts forbidden transition
- **WHEN** a user with COCINA role requests a transition from EN_CAMINO to ENTREGADO
- **THEN** the system returns HTTP 403 Forbidden (role not authorized for this transition)

#### Scenario: PEDIDOS performs all non-admin transitions
- **WHEN** a user with PEDIDOS role requests any non-cancel transition
- **THEN** the system accepts the transition (PEDIDOS has all kitchen + delivery transitions)

### Requirement: Event manager (pub/sub in-process)
The system SHALL provide an `EventManager` class that manages SSE subscriber queues using `asyncio.Queue`. The manager SHALL support subscribe, unsubscribe, and broadcast operations. The broadcast SHALL be non-blocking: if a subscriber's queue is full, that subscriber SHALL be disconnected.

#### Scenario: Subscribe and receive event
- **WHEN** a new SSE client connects and subscribes via EventManager
- **THEN** the client receives all subsequent broadcast events via its queue

#### Scenario: Broadcast with no subscribers
- **WHEN** an event is broadcast and no SSE clients are connected
- **THEN** the event is silently discarded with no error
