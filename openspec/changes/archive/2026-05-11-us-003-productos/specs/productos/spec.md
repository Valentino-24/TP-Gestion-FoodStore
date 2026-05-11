## ADDED Requirements

### Requirement: Create product

The system SHALL allow ADMIN users to create products with a unique nombre, descripcion, precio, categoria_id, and optional imagen_url.

#### Scenario: Successful product creation
- **WHEN** an ADMIN user sends a POST request to /api/v1/productos with valid nombre, descripcion, precio, categoria_id, and optional imagen_url
- **THEN** the system creates a new Producto record, sets activo=true, and returns HTTP 201 with the created product data

#### Scenario: Non-existent categoria_id
- **WHEN** an ADMIN user attempts to create a product with a categoria_id that does not exist
- **THEN** the system returns HTTP 404 with error message indicating the category was not found

#### Scenario: Invalid precio (negative)
- **WHEN** an ADMIN user attempts to create a product with a negative precio
- **THEN** the system returns HTTP 422 with a validation error

#### Scenario: Non-admin creation rejected
- **WHEN** a non-ADMIN authenticated user sends a POST request to /api/v1/productos
- **THEN** the system returns HTTP 403 Forbidden

#### Scenario: Missing required fields
- **WHEN** an ADMIN user sends a POST request without nombre, precio, or categoria_id
- **THEN** the system returns HTTP 422 with validation errors for each missing field

### Requirement: List products

The system SHALL allow any authenticated user to list active products with pagination and optional categoria_id filtering.

#### Scenario: List all active products
- **WHEN** an authenticated user sends a GET request to /api/v1/productos
- **THEN** the system returns HTTP 200 with a paginated list of products where activo=true, ordered by nombre, with default page=1 and size=20

#### Scenario: Filter by categoria_id
- **WHEN** an authenticated user sends a GET request to /api/v1/productos?categoria_id=1
- **THEN** the system returns only products where activo=true AND categoria_id=1

#### Scenario: Pagination navigation
- **WHEN** an authenticated user sends a GET request to /api/v1/productos?page=2&size=10
- **THEN** the system returns products 11-20 (10 per page) with total count in response metadata

#### Scenario: Empty list
- **WHEN** an authenticated user sends a GET request to /api/v1/productos and no active products exist
- **THEN** the system returns HTTP 200 with an empty items array and total=0

#### Scenario: Unauthenticated access
- **WHEN** a request without a valid Bearer token is sent to GET /api/v1/productos
- **THEN** the system returns HTTP 401 Unauthorized

### Requirement: Get product by ID

The system SHALL allow any authenticated user to retrieve a single product by its ID.

#### Scenario: Get existing active product
- **WHEN** an authenticated user sends a GET request to /api/v1/productos/{id} with a valid id
- **THEN** the system returns HTTP 200 with the product data including nombre, descripcion, precio, categoria_id, imagen_url, and activo status

#### Scenario: Get non-existent product
- **WHEN** an authenticated user sends a GET request to /api/v1/productos/{id} with an id that does not exist
- **THEN** the system returns HTTP 404 Not Found

#### Scenario: Get soft-deleted product
- **WHEN** an authenticated user sends a GET request to /api/v1/productos/{id} where the product has activo=false
- **THEN** the system returns HTTP 404 Not Found (soft-deleted products are not accessible via GET)

### Requirement: Update product

The system SHALL allow ADMIN users to update product fields including nombre, descripcion, precio, categoria_id, and imagen_url.

#### Scenario: Successful product update
- **WHEN** an ADMIN user sends a PUT request to /api/v1/productos/{id} with valid updated fields
- **THEN** the system updates the product and returns HTTP 200 with the updated data

#### Scenario: Update non-existent product
- **WHEN** an ADMIN user sends a PUT request to /api/v1/productos/{id} with an id that does not exist
- **THEN** the system returns HTTP 404 Not Found

#### Scenario: Update to non-existent category
- **WHEN** an ADMIN user attempts to update a product's categoria_id to a value that does not exist
- **THEN** the system returns HTTP 404 with error message indicating the category was not found

#### Scenario: Update with invalid precio
- **WHEN** an ADMIN user attempts to update a product's precio to a negative value
- **THEN** the system returns HTTP 422 with a validation error

### Requirement: Delete product (soft delete)

The system SHALL allow ADMIN users to soft-delete a product by setting activo to false.

#### Scenario: Successful soft delete
- **WHEN** an ADMIN user sends a DELETE request to /api/v1/productos/{id}
- **THEN** the system sets activo=false on the product and returns HTTP 204 No Content

#### Scenario: Delete non-existent product
- **WHEN** an ADMIN user sends a DELETE request to /api/v1/productos/{id} with an id that does not exist
- **THEN** the system returns HTTP 404 Not Found

#### Scenario: Re-activate a product
- **WHEN** an ADMIN user updates a deactivated product via PUT
- **THEN** the system sets activo=true and returns the product as active

### Requirement: Product model structure

The producto table SHALL contain id (PK, auto-increment), nombre (VARCHAR(200), NOT NULL, indexed), descripcion (TEXT, nullable), precio (FLOAT, NOT NULL, >= 0), categoria_id (INTEGER, FK to categoria.id, NOT NULL, indexed), imagen_url (VARCHAR(500), nullable), activo (BOOLEAN, default true), creado_en (TIMESTAMP, auto-set), actualizado_en (TIMESTAMP, auto-updated).

#### Scenario: Schema validation
- **WHEN** the migration is applied
- **THEN** the producto table exists with all required columns, constraints, and the foreign key to categoria

#### Scenario: FK integrity on categoria hard-delete
- **WHEN** an attempt is made to hard-delete a categoria row that has products referencing it
- **THEN** the DB constraint prevents the deletion (RESTRICT behavior)

### Requirement: Seed data

The system SHALL provide initial seed data with sample products for each existing category.

#### Scenario: Products are seeded
- **WHEN** the seed command is run
- **THEN** there are products created for each category (at least 2-3 products per category) with realistic food store names and prices
