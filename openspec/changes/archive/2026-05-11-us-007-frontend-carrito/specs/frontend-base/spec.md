## MODIFIED Requirements

### Requirement: Routing structure
The system SHALL implement react-router-dom with three route groups: public routes (no auth required), authenticated routes (token required), and admin routes (ADMIN role required).

#### Scenario: Public routes are accessible without auth
- **WHEN** an unauthenticated user navigates to /login or /register
- **THEN** the page renders without redirect

#### Scenario: Authenticated routes redirect to login
- **WHEN** an unauthenticated user navigates to a protected route (e.g. /productos, /carrito, /checkout, /pedidos)
- **THEN** the system redirects to /login

#### Scenario: Admin routes require ADMIN role
- **WHEN** a non-ADMIN authenticated user navigates to /admin/*
- **THEN** the system redirects to /

#### Scenario: Admin routes are accessible by ADMIN
- **WHEN** an authenticated user with ADMIN role navigates to /admin/*
- **THEN** the admin layout renders correctly

#### Scenario: Cart and checkout routes are protected
- **WHEN** an authenticated user navigates to /carrito or /checkout
- **THEN** the page renders within the authenticated layout

#### Scenario: Orders routes are protected
- **WHEN** an authenticated user navigates to /pedidos or /pedidos/:id
- **THEN** the page renders within the authenticated layout

#### Scenario: Address management route is protected
- **WHEN** an authenticated user navigates to /perfil/direcciones
- **THEN** the page renders within the authenticated layout

## ADDED Requirements

### Requirement: Address management UI
The system SHALL provide a page at `/perfil/direcciones` where authenticated users can manage their shipping addresses with CRUD operations.

#### Scenario: List addresses
- **WHEN** the user navigates to /perfil/direcciones
- **THEN** the page displays a list of saved addresses with edit and delete options

#### Scenario: Add address
- **WHEN** the user clicks "Agregar dirección"
- **THEN** a form is displayed to input address data, which creates a new address via POST /api/v1/direcciones on submit
