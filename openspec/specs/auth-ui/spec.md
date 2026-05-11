# Auth UI

Specification for the frontend authentication user interface — login, registration, logout, and auth state management.

## Requirements

### Requirement: API client with JWT interceptors
The system SHALL provide an axios-based API client that automatically attaches the JWT access token to requests and handles token refresh on 401 responses.

#### Scenario: Access token is attached to requests
- **WHEN** any authenticated request is sent
- **THEN** the `Authorization: Bearer <access_token>` header SHALL be included

#### Scenario: Automatic token refresh on 401
- **WHEN** a request returns HTTP 401
- **THEN** the system attempts to refresh the token using the stored refresh token, and if successful, retries the original request with the new access token

#### Scenario: Redirect to login on refresh failure
- **WHEN** token refresh fails (refresh token expired or revoked)
- **THEN** the system clears auth state and redirects to /login

#### Scenario: Concurrent 401 requests queue
- **WHEN** multiple requests receive 401 simultaneously
- **THEN** only one refresh request is made, and all queued requests retry after successful refresh

### Requirement: User registration UI
The system SHALL provide a registration page at /register with a form for name, email, and password, that calls POST /api/v1/auth/register.

#### Scenario: Successful registration
- **WHEN** a user submits valid registration data
- **THEN** the system stores the returned tokens, updates auth state, and redirects to the home page

#### Scenario: Registration validation errors
- **WHEN** a user submits invalid data (weak password, duplicate email)
- **THEN** the form displays the error message from the API response

### Requirement: User login UI
The system SHALL provide a login page at /login with a form for email and password, that calls POST /api/v1/auth/login.

#### Scenario: Successful login
- **WHEN** a user submits valid credentials
- **THEN** the system stores access_token and refresh_token, updates auth state with user data, and redirects to /
- **AND** the navbar shows the user's name

#### Scenario: Invalid credentials
- **WHEN** a user submits incorrect email or password
- **THEN** the form displays "Credenciales invalidas" error message

#### Scenario: Rate limited
- **WHEN** too many failed login attempts
- **THEN** the form displays the rate limit error message

### Requirement: Auth state management with Zustand
The system SHALL use Zustand for managing authentication state, including the current user, access token, refresh token, and login/register/logout actions.

#### Scenario: Auth store persists tokens
- **WHEN** login or register succeeds
- **THEN** access_token and refresh_token are persisted in localStorage

#### Scenario: Auth store hydrates from localStorage
- **WHEN** the app loads and tokens exist in localStorage
- **THEN** the auth store initializes with the stored tokens and fetches user data via GET /auth/me

#### Scenario: Logout clears state
- **WHEN** a user clicks logout
- **THEN** the auth store calls POST /api/v1/logout, clears tokens from localStorage, and redirects to /login

### Requirement: Logout flow
The system SHALL provide a logout action accessible from the authenticated layout's navbar.

#### Scenario: User logs out from navbar
- **WHEN** an authenticated user clicks "Cerrar sesión" in the navbar
- **THEN** the system calls POST /api/v1/logout with the refresh token, clears auth state, and redirects to /login
