## ADDED Requirements

### Requirement: Orders list page
The system SHALL display the authenticated user's order history at `/pedidos`, fetched from `GET /api/v1/pedidos`.

#### Scenario: Orders list loads
- **WHEN** the user navigates to /pedidos
- **THEN** the system fetches and displays their orders in a list with: pedido ID, date, total, estado (with color-coded badge)

#### Scenario: Empty orders
- **WHEN** the user has no orders
- **THEN** the page displays "No tenés pedidos aún" with a link to the catalog

### Requirement: Order detail page
The system SHALL display full order information at `/pedidos/:id`, fetched from `GET /api/v1/pedidos/{id}`.

#### Scenario: Order detail loads
- **WHEN** the user navigates to /pedidos/:id with a valid ID
- **THEN** the page displays: order items with quantities and prices, total, estado badge, payment info, and shipping address

#### Scenario: Order not found
- **WHEN** the order ID does not exist or belongs to another user
- **THEN** the system displays a 404 message "Pedido no encontrado"

### Requirement: Address management page
The system SHALL provide an address management page at `/perfil/direcciones` with CRUD operations.

#### Scenario: List addresses
- **WHEN** the user navigates to /perfil/direcciones
- **THEN** the system displays a list of saved addresses with edit/delete options

#### Scenario: Add address
- **WHEN** the user clicks "Agregar dirección"
- **THEN** a form is displayed to input address data, which creates a new address on submit

#### Scenario: Edit address
- **WHEN** the user clicks "Editar" on an existing address
- **THEN** a form is displayed pre-filled with the address data, which updates on submit

#### Scenario: Delete address
- **WHEN** the user clicks "Eliminar" on an existing address
- **THEN** the address is soft-deleted and removed from the list
