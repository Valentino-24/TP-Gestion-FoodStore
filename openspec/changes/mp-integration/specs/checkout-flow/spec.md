## MODIFIED Requirements

### Requirement: Checkout page

The system SHALL provide a checkout page at `/checkout` that guides the user through selecting a shipping address, payment method (including Efectivo), reviewing the order summary, and placing the order.

#### Scenario: Checkout with saved addresses and all payment methods
- **WHEN** the user navigates to /checkout with items in the cart
- **THEN** the page shows address selection, payment method selection (including Tarjeta de credito, Tarjeta de debito, and Efectivo), order summary, and a "Realizar pedido" button

#### Scenario: Place order with tarjeta payment
- **WHEN** the user selects Tarjeta as payment method and clicks "Realizar pedido" with valid address
- **THEN** the system creates the pedido, clears the cart, and redirects to `/pago/{pedidoId}` with the MercadoPago card form

#### Scenario: Place order with Efectivo payment
- **WHEN** the user selects Efectivo as payment method and clicks "Realizar pedido" with valid address
- **THEN** the system creates the pedido, clears the cart, and redirects to `/pedidos` (no payment page shown)

## ADDED Requirements

### Requirement: Payment page with card form

The system SHALL show a card payment form when the user is redirected to the payment page after placing an order with tarjeta method.

#### Scenario: Payment page shows order info and card brick
- **WHEN** the user is redirected to `/pago/{pedidoId}` after placing an order with tarjeta
- **THEN** the page shows the order total, pedido ID, and the MercadoPago Card Payment Brick for card data entry
