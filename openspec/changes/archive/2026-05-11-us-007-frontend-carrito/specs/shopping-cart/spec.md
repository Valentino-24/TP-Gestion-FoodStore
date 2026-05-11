## ADDED Requirements

### Requirement: Cart store with Zustand
The system SHALL provide a Zustand store for the shopping cart, persisted in localStorage, with actions to add, remove, update quantity, and clear.

#### Scenario: Add item to cart
- **WHEN** a user clicks "Agregar al carrito" on a product
- **THEN** the item is added to the cart (or quantity incremented if already present)

#### Scenario: Update quantity
- **WHEN** a user changes the quantity of an item in the cart
- **THEN** the store updates the quantity and recalculates the subtotal

#### Scenario: Remove item
- **WHEN** a user clicks the remove button on a cart item
- **THEN** the item is removed from the cart

#### Scenario: Cart persists in localStorage
- **WHEN** the user refreshes the page
- **THEN** the cart items are restored from localStorage

#### Scenario: Cart summary
- **WHEN** the cart has items
- **THEN** the store exposes total items count and total price

### Requirement: Cart page
The system SHALL display the cart contents at `/carrito` with item list, quantities, subtotals, total, and a checkout button.

#### Scenario: Empty cart
- **WHEN** the cart is empty
- **THEN** the page displays "Tu carrito está vacío" with a link to the catalog

#### Scenario: Cart with items
- **WHEN** the cart has items
- **THEN** the page displays each product with image, name, unit price, quantity controls, line total, and a remove button
- **AND** the page shows the total amount and a "Ir al checkout" button
