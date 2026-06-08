## MODIFIED Requirements

### Requirement: Cart store with Zustand
The system SHALL provide a Zustand store for the shopping cart, persisted in localStorage, with actions to add, remove, update quantity, and clear. Data fetching for products, orders, and other server data SHALL use @tanstack/react-query.

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

#### Scenario: Product catalog uses TanStack Query
- **WHEN** the user navigates to the product catalog
- **THEN** product data is fetched via useQuery with loading/error states, not raw useEffect

#### Scenario: Query invalidation on mutations
- **WHEN** a mutation affects product or order data (e.g., creating an order)
- **THEN** related queries are invalidated to refetch fresh data

## ADDED Requirements

### Requirement: Domain-specific hooks with TanStack Query
The system SHALL provide custom hooks wrapping @tanstack/react-query for each domain, encapsulating query keys, stale times, and mutation logic.

#### Scenario: useProductos hook
- **WHEN** a component calls useProductos(filters)
- **THEN** it returns { data, isLoading, isError, error } from useQuery with appropriate queryKey

#### Scenario: usePedidos hook
- **WHEN** a component calls usePedidos()
- **THEN** it returns query result for the user's orders with automatic cache invalidation on mutations

#### Scenario: Mutations invalidate queries
- **WHEN** a mutation completes (e.g., create order)
- **THEN** the onSuccess callback invalidates related queries (e.g., pedidos list, pedido detail)
