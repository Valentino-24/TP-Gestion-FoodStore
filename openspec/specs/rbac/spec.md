# RBAC

Specification for the role-based access control system.

## Requirements

### Requirement: Role-based endpoint protection
The system SHALL protect endpoints by verifying that the authenticated user possesses at least one of the required roles. Requests without a valid token SHALL receive HTTP 401. Requests with a valid token but insufficient roles SHALL receive HTTP 403.

#### Scenario: Unauthenticated access to protected endpoint
- **WHEN** a request is sent to a protected endpoint without a Bearer token
- **THEN** the system returns HTTP 401 Unauthorized

#### Scenario: Insufficient role for protected endpoint
- **WHEN** a user with only the CLIENT role attempts to access an endpoint requiring ADMIN role
- **THEN** the system returns HTTP 403 Forbidden

#### Scenario: Sufficient role for protected endpoint
- **WHEN** a user with the ADMIN role (or any allowed role) accesses an endpoint requiring ADMIN role
- **THEN** the system processes the request normally and returns the appropriate response

#### Scenario: Expired token access
- **WHEN** a user attempts to access a protected endpoint with an expired JWT
- **THEN** the system returns HTTP 401 with a message indicating token expiration

### Requirement: Multiple roles per user
The system SHALL support users having multiple roles simultaneously through a many-to-many relationship between Usuario and Rol via the usuario_rol table.

#### Scenario: User with multiple roles
- **WHEN** a user is assigned both CLIENT and STOCK roles
- **THEN** the user can access endpoints requiring CLIENT role AND endpoints requiring STOCK role

#### Scenario: Role verification checks all assigned roles
- **WHEN** a user with roles [CLIENT, PEDIDOS] accesses an endpoint requiring PEDIDOS
- **THEN** access is granted because the user has at least one of the required roles

### Requirement: Fixed role definitions
The system SHALL use exactly four predefined roles with stable IDs: ADMIN (1), STOCK (2), PEDIDOS (3), CLIENT (4). These roles SHALL be seeded in the database and SHALL NOT be modifiable through the application.

#### Scenario: Role IDs are stable
- **WHEN** the system checks for ADMIN role
- **THEN** it references the role with id=1, not by string comparison alone

#### Scenario: New roles cannot be created
- **WHEN** an attempt is made to create a new role via the application
- **THEN** the system rejects the operation (roles are seed-only data)

### Requirement: Public endpoints require no authentication
The system SHALL allow access to public endpoints without any authentication token. Public endpoints include: catalog browsing, user registration, user login, and token refresh.

#### Scenario: Access to public endpoint without token
- **WHEN** an unauthenticated user sends a request to GET /api/v1/productos
- **THEN** the system returns HTTP 200 with the catalog data

#### Scenario: Access to public registration endpoint
- **WHEN** an unauthenticated user sends a POST request to /api/v1/auth/register
- **THEN** the system processes the registration normally
