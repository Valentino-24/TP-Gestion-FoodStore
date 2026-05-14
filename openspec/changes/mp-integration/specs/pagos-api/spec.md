## MODIFIED Requirements

### Requirement: Initiate payment

The system SHALL initiate a MercadoPago payment for a pedido and return the payment result.

#### Scenario: Create payment with valid card token
- **WHEN** an authenticated user sends POST /api/v1/pagos with pedido_id and mp_token
- **AND** MP_ACCESS_TOKEN is configured (TEST- or APP_USR-)
- **THEN** the system creates a Pago record, calls MercadoPago API with the token, and returns HTTP 201 with the payment status

#### Scenario: Payment without MP credentials
- **WHEN** MP_ACCESS_TOKEN is not configured and a payment is initiated
- **THEN** the system returns HTTP 503 with detail "MercadoPago no configurado"

#### Scenario: Reject payment for non-PENDIENTE pedido
- **WHEN** an authenticated user sends POST /api/v1/pagos for a pedido that is not in PENDIENTE estado
- **THEN** the system returns HTTP 400 with detail "El pedido no está en estado PENDIENTE"

#### Scenario: Efectivo pedido does not require payment
- **WHEN** a pedido is created with forma_pago_id = Efectivo
- **THEN** no Pago record is created and the pedido remains in PENDIENTE until admin confirms it

## ADDED Requirements

### Requirement: Initiate payment with TEST token

The system SHALL process payments using MercadoPago SDK when MP_ACCESS_TOKEN starts with "TEST-" (not treating it as unconfigured).

#### Scenario: Payment with test credentials
- **WHEN** MP_ACCESS_TOKEN starts with "TEST-" and a valid mp_token is provided
- **THEN** the system calls the MercadoPago SDK and returns the payment result from the sandbox environment
