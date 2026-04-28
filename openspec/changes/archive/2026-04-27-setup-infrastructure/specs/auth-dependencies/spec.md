## ADDED Requirements

### Requirement: get_current_user dependency
The application SHALL provide a FastAPI dependency for extracting and validating the current user from JWT.

#### Scenario: Valid token provided
- **WHEN** request includes valid JWT in Authorization header
- **THEN** returns user object from database

#### Scenario: No token provided
- **WHEN** request has no Authorization header
- **THEN** HTTP 401 returned

#### Scenario: Invalid token
- **WHEN** Authorization header contains invalid/expired JWT
- **THEN** HTTP 401 returned

### Requirement: require_role dependency factory
The application SHALL provide a dependency factory for role-based access control.

#### Scenario: User has required role
- **WHEN** user with role ADMIN accesses endpoint requiring ADMIN
- **THEN** request proceeds normally

#### Scenario: User lacks required role
- **WHEN** user with role CLIENT accesses endpoint requiring ADMIN
- **THEN** HTTP 403 returned

#### Scenario: Multiple roles allowed
- **WHEN** user with role PEDIDOS accesses endpoint requiring ADMIN or PEDIDOS
- **THEN** request proceeds normally