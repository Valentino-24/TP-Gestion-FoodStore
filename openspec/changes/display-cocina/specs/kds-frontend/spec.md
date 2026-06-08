# KDS Frontend

Specification for the Kitchen Display System React frontend.

## ADDED Requirements

### Requirement: KDS page with two-column layout
The system SHALL provide a `/cocina` route that renders a two-column layout: "Por preparar" (CONFIRMADO) on the left and "En preparación" (EN_PREP) on the right. Each column SHALL display pedido cards ordered by kitchen entry time ascending (oldest first). The page SHALL only be accessible to users with COCINA, PEDIDOS, or ADMIN roles.

#### Scenario: Access KDS with COCINA role
- **WHEN** a user with COCINA role navigates to /cocina
- **THEN** the system renders the two-column KDS layout

#### Scenario: Access KDS without authorization
- **WHEN** a user with only CLIENT role navigates to /cocina
- **THEN** the system redirects to home or shows HTTP 403

#### Scenario: Initial load shows all kitchen pedidos
- **WHEN** the KDS page mounts
- **THEN** it fetches GET /api/v1/cocina/pedidos and displays all CONFIRMADO and EN_PREP pedidos in their respective columns

### Requirement: Pedido card
The system SHALL display each pedido as a card showing: order number (`id`), items (product `nombre_snapshot` × `cantidad`), ingredient exclusions from `personalizacion`, customer `notas`, kitchen entry timestamp, and elapsed time since entry.

#### Scenario: Card displays order info
- **WHEN** a pedido is displayed in the KDS
- **THEN** its card shows order number, item names with quantities, exclusions, notes, and elapsed time

### Requirement: Urgency timer
The system SHALL display an elapsed time indicator on each pedido card, calculated from the kitchen entry timestamp. The system SHALL apply visual styling based on thresholds: normal (< 10 min), warning (10-20 min, orange), urgent (> 20 min, red). The timer SHALL refresh every 15 seconds in the client.

#### Scenario: Timer shows normal state
- **WHEN** a pedido has been in the kitchen for less than 10 minutes
- **THEN** the card shows normal styling

#### Scenario: Timer shows warning state
- **WHEN** a pedido has been in the kitchen between 10 and 20 minutes
- **THEN** the card shows orange/warning styling

#### Scenario: Timer shows urgent state
- **WHEN** a pedido has been in the kitchen for more than 20 minutes
- **THEN** the card shows red/urgent styling

### Requirement: Real-time updates via SSE
The system SHALL connect to `GET /api/v1/cocina/eventos` via `EventSource` on page mount. The system SHALL handle SSE events to update the UI without page reload:
- `PEDIDO_CONFIRMADO`: add new card to "Por preparar" column
- `PEDIDO_EN_PREPARACION`: move card from "Por preparar" to "En preparación"
- `PEDIDO_EN_CAMINO`: remove card from display
- `PEDIDO_CANCELADO`: remove card from display

#### Scenario: New pedido arrives via SSE
- **WHEN** the KDS receives a `PEDIDO_CONFIRMADO` event
- **THEN** a new card appears in the "Por preparar" column without page reload

#### Scenario: Pedido moves to preparation via SSE
- **WHEN** the KDS receives a `PEDIDO_EN_PREPARACION` event
- **THEN** the card moves from "Por preparar" to "En preparación" column

#### Scenario: Pedido leaves kitchen via SSE
- **WHEN** the KDS receives a `PEDIDO_EN_CAMINO` or `PEDIDO_CANCELADO` event
- **THEN** the card is removed from the display

### Requirement: Take pedido action
The system SHALL provide an "Iniciar preparación" button on pedido cards in the "Por preparar" column. When clicked, the system SHALL send `PATCH /api/v1/pedidos/{id}/estado` with `{"nuevo_estado": "EN_PREP"}` and move the card to the "En preparación" column on success.

#### Scenario: Start preparing a pedido
- **WHEN** the cocinero clicks "Iniciar preparación" on a CONFIRMADO pedido
- **THEN** the system sends PATCH /api/v1/pedidos/{id}/estado with EN_PREP, and on success moves the card to "En preparación"

### Requirement: Mark pedido done action
The system SHALL provide a "Listo" button on pedido cards in the "En preparación" column. When clicked, the system SHALL send `PATCH /api/v1/pedidos/{id}/estado` with `{"nuevo_estado": "EN_CAMINO"}` and remove the card on success.

#### Scenario: Mark pedido as done
- **WHEN** the cocinero clicks "Listo" on a EN_PREP pedido
- **THEN** the system sends PATCH /api/v1/pedidos/{id}/estado with EN_CAMINO, and on success removes the card from the KDS

### Requirement: SSE resilience with polling fallback
The system SHALL detect SSE disconnection and display an indicator "sin conexión en vivo". While disconnected, the system SHALL poll `GET /api/v1/cocina/pedidos` every 30 seconds. When SSE reconnects, the system SHALL resume push mode and perform a full refresh of all pedidos.

#### Scenario: SSE disconnects
- **WHEN** the SSE connection is lost
- **THEN** the KDS shows a "sin conexión en vivo" indicator and starts polling every 30 seconds

#### Scenario: SSE reconnects
- **WHEN** the SSE connection is re-established after a disconnection
- **THEN** the KDS performs a full fetch of GET /api/v1/cocina/pedidos and resumes push mode

### Requirement: Incoming order alert (optional)
The system SHALL provide an audible beep and brief visual flash when a `PEDIDO_CONFIRMADO` event is received. The sound SHALL use the Web Audio API (no external files). The system SHALL include a toggle to mute/unmute the sound, persisted to `localStorage`.

#### Scenario: Sound plays on new pedido
- **WHEN** the KDS receives a PEDIDO_CONFIRMADO event and sound is enabled
- **THEN** the system plays a beep via Web Audio API and shows a visual flash

#### Scenario: Sound toggle persists
- **WHEN** the user toggles sound OFF
- **THEN** the preference is saved to localStorage and no sound plays on subsequent events

### Requirement: No auto-logout on KDS
The system SHALL exclude the `/cocina` route from any auto-logout or session timeout mechanism. The KDS SHALL remain active during the entire kitchen shift.

#### Scenario: KDS stays active
- **WHEN** a cocinero is on the /cocina page
- **THEN** the session does not time out due to inactivity
