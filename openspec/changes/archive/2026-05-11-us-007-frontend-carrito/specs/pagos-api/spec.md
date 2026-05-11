## ADDED Requirements

### Requirement: Initiate payment
The system SHALL initiate a MercadoPago payment for a pedido and return the payment URL or instruction for the frontend.

#### Scenario: Create payment for pedido
- **WHEN** an authenticated user sends POST /api/v1/pagos with pedido_id and payment method data
- **THEN** the system creates a Pago record, calls MercadoPago API, and returns HTTP 201 with payment URL or instruction

#### Scenario: Payment without MP credentials
- **WHEN** MP_ACCESS_TOKEN is not configured and a payment is initiated
- **THEN** the system either uses a simulated payment flow or returns HTTP 503

### Requirement: Payment webhook
The system SHALL receive MercadoPago webhook notifications to update pedido estado upon payment confirmation.

#### Scenario: Payment confirmed via webhook
- **WHEN** MercadoPago sends a POST to /api/v1/webhooks/mercadopago with payment.id and status="approved"
- **THEN** the system updates the Pago record and transitions the Pedido to CONFIRMADO

#### Scenario: Payment rejected via webhook
- **WHEN** MercadoPago sends a webhook with status="rejected" or "cancelled"
- **THEN** the system updates the Pago record and the Pedido remains in PENDIENTE (or transitions to CANCELADO)
