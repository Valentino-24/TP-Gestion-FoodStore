## ADDED Requirements

### Requirement: Admin productos page
The system SHALL provide a product management page at `/admin/productos` with a paginated table, search, and CRUD operations.

#### Scenario: Products table loads
- **WHEN** an ADMIN user navigates to /admin/productos
- **THEN** the page displays a paginated table of products with columns: nombre, precio, categoría, activo, acciones

#### Scenario: Create product
- **WHEN** an ADMIN user clicks "Nuevo producto" and submits the form
- **THEN** the system creates the product via POST /api/v1/productos/ and the table refreshes

#### Scenario: Edit product
- **WHEN** an ADMIN user clicks "Editar" on a product row and submits changes
- **THEN** the system updates the product via PUT /api/v1/productos/{id} and the table refreshes

#### Scenario: Delete product (soft-delete)
- **WHEN** an ADMIN user clicks "Eliminar" on a product row and confirms
- **THEN** the system soft-deletes via DELETE /api/v1/productos/{id} and the table refreshes

### Requirement: Admin categorias page
The system SHALL provide a category management page at `/admin/categorias` with a table and CRUD operations.

#### Scenario: Categories table loads
- **WHEN** an ADMIN user navigates to /admin/categorias
- **THEN** the page displays a table of categories with columns: nombre, descripcion, activo, acciones

#### Scenario: Create category
- **WHEN** an ADMIN user clicks "Nueva categoría" and submits the form
- **THEN** the system creates the category via POST /api/v1/categorias/ and the table refreshes

#### Scenario: Edit category
- **WHEN** an ADMIN user clicks "Editar" on a category row and submits changes
- **THEN** the system updates the category via PUT /api/v1/categorias/{id} and the table refreshes

#### Scenario: Delete category (soft-delete)
- **WHEN** an ADMIN user clicks "Eliminar" on a category row and confirms
- **THEN** the system soft-deletes via DELETE /api/v1/categorias/{id} and the table refreshes

### Requirement: Admin clientes page
The system SHALL provide a client list page at `/admin/clientes` with pagination and search.

#### Scenario: Clients table loads
- **WHEN** an ADMIN user navigates to /admin/clientes
- **THEN** the page displays a paginated table of clients with columns: nombre, apellido, email, teléfono, activo

### Requirement: Admin pedidos page
The system SHALL provide an order management page at `/admin/pedidos` with list, filter by estado, and FSM state transition.

#### Scenario: Orders table loads
- **WHEN** an ADMIN user navigates to /admin/pedidos
- **THEN** the page displays a paginated table of all orders with: ID, usuario, total, estado, fecha, acciones

#### Scenario: Filter orders by estado
- **WHEN** an ADMIN user selects a estado filter
- **THEN** the table refreshes showing only orders matching that estado

#### Scenario: Change order estado
- **WHEN** an ADMIN user selects a valid target estado from the dropdown on an order row
- **THEN** the system calls PATCH /api/v1/pedidos/{id}/estado and the table refreshes
