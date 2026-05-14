## ADDED Requirements

### Requirement: Card payment form with MercadoPago Brick

The system SHALL provide a card payment form using MercadoPago Card Payment Brick on the payment page.

#### Scenario: Show card form on payment page
- **WHEN** the user navigates to `/pago/{pedidoId}` with a pedido that has a tarjeta forma_pago
- **THEN** the page shows the MercadoPago Card Payment Brick with inputs for card number, expiration date, CVV, and cardholder name

#### Scenario: Successful token generation
- **WHEN** the user fills valid card data and submits the form
- **THEN** MercadoPago generates a card token and the system calls POST /api/v1/pagos with the token

#### Scenario: Payment approved
- **WHEN** the backend returns estado="aprobado"
- **THEN** the page shows a success message with a link to view the pedido

#### Scenario: Payment rejected
- **WHEN** the backend returns estado="rechazado" or mp_status indicates rejection
- **THEN** the page shows an error message and allows the user to retry

#### Scenario: Invalid card data
- **WHEN** the user submits invalid card data
- **THEN** the Card Payment Brick shows inline validation errors and does not generate a token
