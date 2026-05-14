# User Authentication

Delta specification for user authentication — adding automatic Cliente creation on registration.

## ADDED Requirements

### Requirement: Automatic Cliente creation on registration
The system SHALL automatically create a `Cliente` record during user registration, using the same nombre, apellido, and email provided in the registration request, so the user has a customer profile immediately after registering.

#### Scenario: Cliente created on register
- **WHEN** a new user registers with nombre, apellido, email, and password
- **THEN** the system creates a `Cliente` record with matching nombre, apellido, and email within the same transaction, and the user can access `GET /clientes/me` immediately after registration without errors

#### Scenario: Registration rollback on Cliente failure
- **WHEN** the Cliente creation fails during registration (e.g., database constraint violation)
- **THEN** the entire registration is rolled back (Usuario and UsuarioRol are not created) and the system returns HTTP 500
