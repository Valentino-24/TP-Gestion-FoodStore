## ADDED Requirements

### Requirement: Create category
The system SHALL allow ADMIN users to create product categories with a unique name and optional description.

#### Scenario: Successful category creation
- **WHEN** an ADMIN user sends a POST request to /api/v1/categorias with a valid nombre and descripcion
- **THEN** the system creates a new Categoria record, sets activo=true, and returns HTTP 201 with the created category

#### Scenario: Duplicate category name
- **WHEN** an ADMIN user attempts to create a category with a nombre that already exists
- **THEN** the system returns HTTP 409 with error message indicating the category already exists

#### Scenario: Non-admin creation rejected
- **WHEN** a non-ADMIN authenticated user sends a POST request to /api/v1/categorias
- **THEN** the system returns HTTP 403 Forbidden

### Requirement: List categories
The system SHALL allow any authenticated user to list all active categories.

#### Scenario: List all active categories
- **WHEN** an authenticated user sends a GET request to /api/v1/categorias
- **THEN** the system returns HTTP 200 with an array of categories where activo=true, ordered by nombre

#### Scenario: Unauthenticated access
- **WHEN** a request without a valid Bearer token is sent to GET /api/v1/categorias
- **THEN** the system returns HTTP 401 Unauthorized

### Requirement: Get category by ID
The system SHALL allow any authenticated user to retrieve a single category by its ID.

#### Scenario: Get existing active category
- **WHEN** an authenticated user sends a GET request to /api/v1/categorias/{id} with a valid id
- **THEN** the system returns HTTP 200 with the category data

#### Scenario: Get non-existent category
- **WHEN** an authenticated user sends a GET request to /api/v1/categorias/{id} with an id that does not exist
- **THEN** the system returns HTTP 404 Not Found

### Requirement: Update category
The system SHALL allow ADMIN users to update category name and description.

#### Scenario: Successful category update
- **WHEN** an ADMIN user sends a PUT request to /api/v1/categorias/{id} with a valid nombre and descripcion
- **THEN** the system updates the category and returns HTTP 200 with the updated data

#### Scenario: Update to duplicate name
- **WHEN** an ADMIN user attempts to update a category to a nombre that already exists
- **THEN** the system returns HTTP 409 with error message

### Requirement: Delete category (soft delete)
The system SHALL allow ADMIN users to soft-delete a category by setting activo to false.

#### Scenario: Successful soft delete
- **WHEN** an ADMIN user sends a DELETE request to /api/v1/categorias/{id}
- **THEN** the system sets activo=false on the category and returns HTTP 204 No Content

#### Scenario: Re-activate a category
- **WHEN** an ADMIN user updates a deactivated category
- **THEN** the system sets activo=true and returns the category as active

### Requirement: Category model structure
The categoria table SHALL contain id (PK, auto-increment), nombre (VARCHAR, unique, indexed), descripcion (TEXT, nullable), activo (BOOLEAN, default true), creado_en (TIMESTAMP, auto-set), actualizado_en (TIMESTAMP, auto-updated).

#### Scenario: Schema validation
- **WHEN** the migration is applied
- **THEN** the categoria table exists with all required columns and constraints
