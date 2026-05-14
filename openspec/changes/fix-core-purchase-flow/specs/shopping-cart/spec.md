# Shopping Cart

Delta specification for the shopping cart — adding cart integration from product catalog.

## ADDED Requirements

### Requirement: Add to cart from product catalog
The system SHALL integrate the cart store with the product catalog so users can add items via the product list grid and the product detail page.

#### Scenario: Add from product card
- **WHEN** the user clicks "Agregar al carrito" on a product card in the grid
- **THEN** `useCart().addItem()` is called with the product's id, name, price, and image, and the cart badge updates

#### Scenario: Add from product detail
- **WHEN** the user selects a quantity and clicks "Agregar al carrito" on the product detail page
- **THEN** `useCart().addItem()` is called with the specified quantity, and the user sees visual feedback (button text changes briefly)
