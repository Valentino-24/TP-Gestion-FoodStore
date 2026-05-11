## ADDED Requirements

### Requirement: Checkout page
The system SHALL provide a checkout page at `/checkout` that guides the user through selecting a shipping address, payment method, reviewing the order summary, and placing the order.

#### Scenario: Checkout with saved addresses
- **WHEN** the user navigates to /checkout with items in the cart
- **THEN** the page shows address selection (dropdown of saved addresses), payment method selection, order summary, and a "Realizar pedido" button

#### Scenario: Add new address during checkout
- **WHEN** the user has no saved addresses or clicks "Agregar dirección"
- **THEN** the page shows an address form inline or in a modal

#### Scenario: Place order successfully
- **WHEN** the user clicks "Realizar pedido" with valid address and payment method
- **THEN** the system creates the pedido via POST /api/v1/pedidos, clears the cart, and redirects to the payment page or order confirmation

#### Scenario: Empty cart checkout
- **WHEN** the user navigates to /checkout with an empty cart
- **THEN** the page redirects to /carrito or shows a message "No hay items para checkout"

### Requirement: Payment page
The system SHALL redirect the user to a payment page after placing the order, where they can complete the payment.

#### Scenario: Payment page shows order info
- **WHEN** the user is redirected to the payment page after placing an order
- **THEN** the page shows the order total, pedido ID, and payment instructions or MercadoPago integration
