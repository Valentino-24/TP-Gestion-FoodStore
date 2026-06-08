## ADDED Requirements

### Requirement: Order history append-only audit trail
The system SHALL record every estado transition of a Pedido in the HistorialEstadoPedido table. The table SHALL be append-only — only INSERT operations are allowed, never UPDATE or DELETE.

#### Scenario: Initial history record on order creation
- **WHEN** a Pedido is created with estado PENDIENTE
- **THEN** a HistorialEstadoPedido record is created with estado_desde=NULL, estado_hasta="PENDIENTE", usuario_id=NULL (system)

#### Scenario: History record on state transition
- **WHEN** a Pedido transitions from CONFIRMADO to EN_PREPARACION
- **THEN** a HistorialEstadoPedido record is created with estado_desde="CONFIRMADO", estado_hasta="EN_PREPARACION", usuario_id=<user who performed transition>

#### Scenario: History returned in pedido detail
- **WHEN** an authenticated user requests GET /api/v1/pedidos/{id}
- **THEN** the response includes a "historial" array ordered by created_at ASC

### Requirement: Snapshot pattern for order items
The system SHALL capture immutable snapshots of price when creating a Pedido. The precio_unitario field in DetallePedido SHALL store the price at the time of order creation, not the current product price.

#### Scenario: Price snapshot on order creation
- **WHEN** a Pedido is created with items
- **THEN** each DetallePedido record stores precio_unitario as the product's current price at the moment of creation

#### Scenario: Price changes don't affect existing orders
- **WHEN** a product's price changes after an order is created
- **THEN** the existing order's DetallePedido records retain the original price_snapshot

### Requirement: Snapshot pattern for shipping address
The system SHALL capture an immutable snapshot of the delivery address when creating a Pedido.

#### Scenario: Address snapshot on order creation
- **WHEN** a Pedido is created with a direccion_id
- **THEN** the system captures a JSON snapshot of the address fields (calle, numero, ciudad, provincia, codigo_postal) and stores it in direccion_snapshot on the Pedido

#### Scenario: Address changes don't affect existing orders
- **WHEN** a user modifies or deletes a direccion after an order is created
- **THEN** the existing order's direccion_snapshot remains unchanged

### Requirement: Atomic stock decrement on order confirmation
The system SHALL decrement product stock atomically when a Pedido transitions from PENDIENTE to CONFIRMADO. The operation SHALL use SELECT FOR UPDATE within a Unit of Work transaction.

#### Scenario: Stock decremented on confirmation
- **WHEN** a Pedido is confirmed (PENDIENTE → CONFIRMADO)
- **THEN** stock_cantidad is decremented by the ordered quantity for each product in the order

#### Scenario: Insufficient stock prevents confirmation
- **WHEN** a product in the order has stock_cantidad < ordered quantity
- **THEN** the transition fails with HTTP 400 and no stock changes are made

### Requirement: Atomic stock restore on order cancellation
The system SHALL restore product stock atomically when a CONFIRMED Pedido is cancelled.

#### Scenario: Stock restored on cancellation
- **WHEN** a CONFIRMED Pedido is cancelled
- **THEN** stock_cantidad is incremented by the ordered quantity for each product in the order
