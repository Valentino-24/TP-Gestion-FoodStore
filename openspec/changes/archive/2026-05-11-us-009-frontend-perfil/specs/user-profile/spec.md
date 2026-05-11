## ADDED Requirements

### Requirement: User profile page
The system SHALL provide a profile page at `/perfil` where the authenticated user can view and edit their personal information.

#### Scenario: Profile loads user data
- **WHEN** an authenticated user navigates to `/perfil`
- **THEN** the system fetches the user's profile via `GET /api/v1/clientes/me` and displays: nombre, apellido, email, teléfono

#### Scenario: Profile loading state
- **WHEN** the profile data is loading
- **THEN** the page shows skeleton/animated placeholders for each field

#### Scenario: Profile not found
- **WHEN** the user has no customer profile (`GET /me` returns 404)
- **THEN** the page shows a message indicating no profile exists with instructions to contact an administrator

#### Scenario: Profile error state
- **WHEN** the profile endpoint fails (network error, 5xx)
- **THEN** the page shows an error message with a retry button

### Requirement: Edit own profile
The system SHALL allow the authenticated user to update their own profile via `PUT /api/v1/clientes/me`.

#### Scenario: Edit profile successfully
- **WHEN** the user modifies nombre, apellido, email, or teléfono and submits the form
- **THEN** the system sends `PUT /api/v1/clientes/me` with the updated fields and displays the updated data with a success message

#### Scenario: Email already taken
- **WHEN** the user changes their email to one already registered by another customer
- **THEN** the system returns 422 and the form shows a clear error message about the duplicate email

#### Scenario: Cancel edit
- **WHEN** the user clicks "Cancelar" while editing
- **THEN** the form reverts to display mode showing the original data

### Requirement: Navbar profile link
The system SHALL provide a link to the profile page in the authenticated user's navigation.

#### Scenario: Navbar shows profile link
- **WHEN** an authenticated user views the navbar
- **THEN** a link or icon labeled "Mi Perfil" is visible and navigates to `/perfil`
