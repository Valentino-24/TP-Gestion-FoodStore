# Frontend Testing

Specification for automated frontend testing — component tests with Vitest + Testing Library and store tests for Zustand.

## ADDED Requirements

### Requirement: Frontend test infrastructure
The system SHALL provide a Vitest-based test suite with jsdom environment and Testing Library for component tests.

#### Scenario: Vitest configuration exists
- **WHEN** the developer runs `npx vitest run` in the `frontend/` directory
- **WHEN** the developer runs `npx vitest` (watch mode)
- **THEN** vitest discovers and runs all `.test.tsx` files in the project

#### Scenario: jsdom environment is configured
- **WHEN** tests render React components
- **THEN** the jsdom environment supports standard DOM APIs (document, window, localStorage)

### Requirement: Auth store tests (Zustand)
The system SHALL test the auth store (authStore.ts) covering login, registration, token management, logout, and state transitions.

#### Scenario: Login updates state correctly
- **WHEN** the auth store's login action is called with valid credentials
- **THEN** the store updates user state and tokens, and isAuthenticated returns true

#### Scenario: Login failure does not mutate state
- **WHEN** the auth store's login action fails (wrong credentials)
- **THEN** the store state remains unchanged and isAuthenticated remains false

#### Scenario: Registration updates state
- **WHEN** the auth store's register action succeeds
- **THEN** the store updates user state and tokens

#### Scenario: Logout clears state
- **WHEN** the auth store's logout action is called
- **THEN** the store clears user data and tokens, and isAuthenticated returns false

#### Scenario: Token refresh updates tokens
- **WHEN** the auth store's refresh action is called with a valid refresh token
- **THEN** the store updates access_token and refresh_token

#### Scenario: State is loaded from localStorage on init
- **WHEN** the auth store is initialized and persisted tokens exist in localStorage
- **THEN** the store restores the tokens and sets isAuthenticated to true

#### Scenario: Logout clears localStorage
- **WHEN** the auth store's logout action is called
- **THEN** localStorage tokens are removed

### Requirement: Cart store tests (Zustand)
The system SHALL test the cart store (cartStore.ts) covering add, remove, quantity update, totals, and localStorage persistence.

#### Scenario: Add item to empty cart
- **WHEN** an item is added to an empty cart
- **THEN** the cart contains one item with quantity 1

#### Scenario: Add duplicate item increments quantity
- **WHEN** an item already in the cart is added again
- **THEN** the quantity of that item is incremented (not duplicated)

#### Scenario: Update item quantity
- **WHEN** the quantity of a cart item is changed
- **THEN** the store updates the quantity and recalculates totals

#### Scenario: Remove item from cart
- **WHEN** an item is removed from the cart
- **THEN** the cart no longer contains that item

#### Scenario: Clear cart
- **WHEN** clearCart is called
- **THEN** the cart is empty

#### Scenario: Cart totals are correct
- **WHEN** the cart contains items with different quantities and prices
- **THEN** totalItems and totalPrice reflect the correct values

#### Scenario: Cart persists to localStorage
- **WHEN** items are added to the cart
- **THEN** the cart state is persisted in localStorage

#### Scenario: Cart restores from localStorage
- **WHEN** the store initializes with persisted cart data in localStorage
- **THEN** the cart state is restored

### Requirement: API client tests (axios interceptors)
The system SHALL test the apiClient (apiClient.ts) covering request interceptor (JWT header), response interceptor (auto-refresh on 401), and token management.

#### Scenario: Request interceptor adds Bearer token
- **WHEN** an API request is made with a stored access token
- **THEN** the Authorization header is set to "Bearer <token>"

#### Scenario: Request interceptor omits token when absent
- **WHEN** an API request is made without a stored access token
- **THEN** the Authorization header is not set

#### Scenario: Response interceptor refreshes on 401
- **WHEN** a 401 response is received and a refresh token exists
- **THEN** the interceptor attempts to refresh the token and retries the original request

#### Scenario: Response interceptor redirects on failed refresh
- **WHEN** a 401 response is received and the refresh attempt fails
- **THEN** the interceptor clears tokens and redirects to /login

#### Scenario: Token helpers work correctly
- **WHEN** storeTokens is called with access and refresh tokens
- **THEN** they are stored in localStorage
- **WHEN** clearTokens is called
- **THEN** both tokens are removed from localStorage

### Requirement: Component tests
The system SHALL test key React components covering rendering, user interactions, loading states, empty states, and error handling.

#### Scenario: ProductCard renders product info
- **WHEN** a ProductCard component receives a valid product prop
- **THEN** it renders the product name, price, category badge, and image

#### Scenario: ProductCard handles missing image
- **WHEN** a ProductCard component receives a product without an image
- **THEN** it renders a placeholder image or hides the image element

#### Scenario: LoginPage renders form
- **WHEN** the LoginPage component renders
- **THEN** it displays email and password inputs and a submit button

#### Scenario: LoginPage shows validation errors
- **WHEN** the user submits the login form with empty fields
- **THEN** validation error messages are displayed

#### Scenario: Navbar shows user name when authenticated
- **WHEN** the user is authenticated
- **THEN** the Navbar displays the user's name and a logout button

#### Scenario: Navbar shows login link when unauthenticated
- **WHEN** the user is not authenticated
- **THEN** the Navbar does not display user-specific elements

#### Scenario: ProtectedRoute redirects unauthenticated users
- **WHEN** an unauthenticated user tries to access a protected route
- **THEN** ProtectedRoute redirects to /login

#### Scenario: ProtectedRoute renders children for authenticated users
- **WHEN** an authenticated user accesses a protected route
- **THEN** ProtectedRoute renders the child components

#### Scenario: Pagination component shows page controls
- **WHEN** the Pagination component receives total pages > 1
- **THEN** it renders page numbers and navigation buttons

#### Scenario: Pagination disables previous on first page
- **WHEN** the current page is 1
- **THEN** the "Anterior" button is disabled

#### Scenario: Pagination disables next on last page
- **WHEN** the current page is the last page
- **THEN** the "Siguiente" button is disabled
