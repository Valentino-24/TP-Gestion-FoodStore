## ADDED Requirements

### Requirement: Product list page
The system SHALL display a paginated grid of all active products at `/productos`, fetched from `GET /api/v1/productos/`.

#### Scenario: Products load successfully
- **WHEN** the user navigates to `/productos`
- **THEN** the system fetches products from the API and displays them in a responsive grid with name, price, category badge, and image

#### Scenario: Loading state
- **WHEN** products are being fetched
- **THEN** the system displays a loading skeleton or spinner

#### Scenario: Empty catalog
- **WHEN** no products are returned by the API
- **THEN** the system displays an empty state message "No hay productos disponibles"

#### Scenario: API error
- **WHEN** the API request fails
- **THEN** the system displays an error message with a retry button

### Requirement: Pagination
The system SHALL paginate the product list using the `page` and `size` query parameters, with controls to navigate between pages.

#### Scenario: Page navigation
- **WHEN** the user clicks "Siguiente" or a page number
- **THEN** the system fetches the corresponding page and updates the grid

#### Scenario: Page info display
- **WHEN** products are displayed
- **THEN** the system shows "Mostrando X-Y de Z productos" and page numbers

#### Scenario: Previous button disabled on first page
- **WHEN** the user is on page 1
- **THEN** the "Anterior" button is disabled

### Requirement: Category filter
The system SHALL allow users to filter products by category using a dropdown, sending `categoria_id` as a query parameter.

#### Scenario: Filter by category
- **WHEN** the user selects a category from the dropdown
- **THEN** the system fetches products filtered by that category and resets to page 1

#### Scenario: Clear filter
- **WHEN** the user selects "Todas las categorías"
- **THEN** the system fetches all products without category filter

### Requirement: Product detail page
The system SHALL display full product information at `/productos/:id`, fetched from `GET /api/v1/productos/{id}`.

#### Scenario: Product loads successfully
- **WHEN** the user navigates to `/productos/:id` with a valid ID
- **THEN** the system displays the product name, description, price, category, image, and a loading state while fetching

#### Scenario: Product not found
- **WHEN** the product ID does not exist
- **THEN** the system displays a 404 message "Producto no encontrado"

#### Scenario: Back navigation
- **WHEN** the user is on the product detail page
- **THEN** a "Volver al catálogo" link navigates back to `/productos`

### Requirement: Featured products on home
The system SHALL display a section of featured products (first 4 active products) on the home page at `/`.

#### Scenario: Home shows featured products
- **WHEN** an authenticated user visits `/`
- **THEN** the home page displays up to 4 products in a mini-grid with a "Ver catálogo completo" link
