# Product Catalog

Delta specification for the product catalog — adding "add to cart" and category name display.

## ADDED Requirements

### Requirement: Add to cart from product list
The system SHALL provide an "Agregar al carrito" button on each product card in the grid, allowing users to add items directly from the list without navigating to the detail page.

#### Scenario: Add to cart from product card
- **WHEN** the user clicks "Agregar al carrito" on a product card
- **THEN** the item is added to the cart with quantity 1 (or incremented if already present) and the cart badge in the navbar updates

### Requirement: Add to cart from product detail
The system SHALL provide a quantity selector and "Agregar al carrito" button on the product detail page, allowing users to specify quantity before adding.

#### Scenario: Add to cart from detail page
- **WHEN** the user selects a quantity and clicks "Agregar al carrito" on the product detail page
- **THEN** the item is added to the cart with the specified quantity (or incremented if already present)

### Requirement: Category name display
The system SHALL display the category name (e.g., "Bebidas") instead of the numeric category ID in product cards and the product detail page.

#### Scenario: Category name in product card
- **WHEN** a product card is rendered
- **THEN** it displays the category name resolved from the categories API, falling back to "Cat. {id}" if the lookup fails

#### Scenario: Category name in product detail
- **WHEN** the product detail page is rendered
- **THEN** it displays the category name instead of the numeric ID
