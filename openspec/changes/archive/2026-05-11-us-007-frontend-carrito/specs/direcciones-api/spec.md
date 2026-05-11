## ADDED Requirements

### Requirement: Direccion model
The system SHALL provide a Direccion model with fields: id, usuario_id (FK), calle, numero, ciudad, provincia, codigo_postal, telefono_contacto, activo, creado_en, actualizado_en.

### Requirement: CRUD direcciones
The system SHALL allow authenticated users to create, list, update, and soft-delete their own addresses.

#### Scenario: Create direccion
- **WHEN** an authenticated user sends POST /api/v1/direcciones with valid address data
- **THEN** the system creates a Direccion asociada to the user and returns HTTP 201

#### Scenario: List user's direcciones
- **WHEN** an authenticated user sends GET /api/v1/direcciones
- **THEN** the system returns HTTP 200 with only that user's active addresses

#### Scenario: Update direccion
- **WHEN** an authenticated user sends PUT /api/v1/direcciones/{id} with valid data
- **THEN** the system updates the address (only if it belongs to the user) and returns HTTP 200

#### Scenario: Delete direccion (soft-delete)
- **WHEN** an authenticated user sends DELETE /api/v1/direcciones/{id}
- **THEN** the system sets activo=False and returns HTTP 204

#### Scenario: Cannot access other user's direccion
- **WHEN** a user attempts to GET/PUT/DELETE a direccion belonging to another user
- **THEN** the system returns HTTP 404 (not found)
