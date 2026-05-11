# User Authentication

Specification for user registration, login, token management, and profile retrieval.

## Requirements

### Requirement: User registration
The system SHALL allow new users to register with name, email, and password. Upon successful registration, the user SHALL be automatically assigned the CLIENT role and SHALL receive an access token (30 min) and a refresh token (7 days).

#### Scenario: Successful registration
- **WHEN** an unregistered user submits a valid registration request with nombre, apellido, email, and password (min 8 chars)
- **THEN** the system creates a Usuario record with hashed password (bcrypt cost >= 10), assigns the CLIENT role, and returns HTTP 201 with access_token, refresh_token, token_type, and expires_in

#### Scenario: Duplicate email rejection
- **WHEN** a user attempts to register with an email that already exists in the system
- **THEN** the system returns HTTP 409 with error message "El email ya esta registrado"

#### Scenario: Weak password rejection
- **WHEN** a user attempts to register with a password shorter than 8 characters
- **THEN** the system returns HTTP 422 with a validation error indicating minimum password length

#### Scenario: Automatic CLIENT role assignment
- **WHEN** a new user registers successfully
- **THEN** the system assigns the CLIENT role (id=4) automatically without the role being sent in the request

### Requirement: User login
The system SHALL authenticate users with email and password, returning a JWT access token and an opaque refresh token. The login response SHALL NOT differentiate between "email not found" and "incorrect password" for security.

#### Scenario: Successful login
- **WHEN** a registered user submits valid email and password
- **THEN** the system returns HTTP 200 with access_token (JWT, 30 min, containing userId, email, roles), refresh_token (UUID v4, 7 days), token_type="bearer", and expires_in

#### Scenario: Invalid credentials
- **WHEN** a user submits incorrect email or password
- **THEN** the system returns HTTP 401 with generic message "Credenciales invalidas" without revealing whether the email exists

#### Scenario: Rate limiting exceeded
- **WHEN** a user (or any user from the same IP) exceeds 5 failed login attempts within 15 minutes
- **THEN** the system returns HTTP 429 with message "Demasiados intentos, reintenta en X minutos"

#### Scenario: Login response includes roles
- **WHEN** a user with multiple roles logs in successfully
- **THEN** the access token JWT payload contains all assigned roles

### Requirement: Token refresh
The system SHALL allow users to obtain a new access token by submitting a valid refresh token. The system SHALL apply token rotation: the old refresh token is invalidated and a new one is issued. The system SHALL detect replay attacks by tracking token family IDs.

#### Scenario: Successful token refresh
- **WHEN** a user submits a valid, non-expired, non-revoked refresh token
- **THEN** the system invalidates the submitted refresh token, creates a new refresh token with a new family_id (or same family if rotation), and returns a new pair of access_token and refresh_token

#### Scenario: Expired refresh token
- **WHEN** a user submits a refresh token that has passed its 7-day expiration
- **THEN** the system returns HTTP 401 and the user must re-authenticate via login

#### Scenario: Revoked refresh token
- **WHEN** a user submits a refresh token that was previously revoked (e.g., via logout)
- **THEN** the system returns HTTP 401

#### Scenario: Replay attack detection
- **WHEN** a user submits a refresh token that has already been used in a previous rotation (same family_id)
- **THEN** the system revokes ALL refresh tokens for that user and returns HTTP 401, forcing re-authentication

### Requirement: User logout
The system SHALL allow authenticated users to log out by revoking their current refresh token.

#### Scenario: Successful logout
- **WHEN** an authenticated user submits their refresh token to the logout endpoint
- **THEN** the system sets revoked_at on the refresh token record and returns HTTP 204 No Content

#### Scenario: Logout with invalid token
- **WHEN** a user submits a refresh token that does not exist or is already revoked
- **THEN** the system returns HTTP 204 (idempotent — no error to avoid information leakage)

### Requirement: Get current user
The system SHALL provide an endpoint for authenticated users to retrieve their own profile information, including name, email, and assigned roles.

#### Scenario: Authenticated user retrieves profile
- **WHEN** an authenticated user sends a GET request to /auth/me with a valid Bearer token
- **THEN** the system returns HTTP 200 with UserResponse containing id, nombre, apellido, email, and roles

#### Scenario: Unauthenticated access
- **WHEN** an unauthenticated user sends a GET request to /auth/me without a valid Bearer token
- **THEN** the system returns HTTP 401

### Requirement: Password hashing
The system SHALL hash all passwords using bcrypt with a cost factor of at least 10. Passwords SHALL NEVER be stored in plain text.

#### Scenario: Password is hashed on registration
- **WHEN** a user registers with password "miPassword123"
- **THEN** the database stores a bcrypt hash, not the plain text password

#### Scenario: Password verification
- **WHEN** a user logs in with the correct password
- **THEN** bcrypt.verify() confirms the password matches the stored hash

### Requirement: JWT access token structure
The system SHALL issue JWT access tokens signed with HS256 containing the userId (sub), email, roles array, and expiration (exp). The token expiration SHALL be 30 minutes from issuance.

#### Scenario: Token contains required claims
- **WHEN** a user successfully logs in
- **THEN** the JWT payload contains: sub (user_id), email, roles (array of role names), exp (expiration timestamp), iat (issued-at timestamp)

#### Scenario: Token expires after 30 minutes
- **WHEN** a user attempts to use an access token 31 minutes after issuance
- **THEN** the system returns HTTP 401 indicating token expiration
