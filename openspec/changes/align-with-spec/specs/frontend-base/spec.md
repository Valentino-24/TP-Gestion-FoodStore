## ADDED Requirements

### Requirement: Payment store (Zustand)
The system SHALL provide a paymentStore (Zustand) to track the state of the MercadoPago payment process. This store SHALL NOT persist to localStorage.

#### Scenario: Payment state is idle initially
- **WHEN** the PaymentPage loads
- **THEN** paymentStore.status is "idle"

#### Scenario: Payment state transitions
- **WHEN** the user submits card data for payment
- **THEN** paymentStore.status transitions through "processing" → "approved" | "rejected" | "error"

#### Scenario: Payment state resets on page reload
- **WHEN** the user reloads the page during payment
- **THEN** paymentStore resets to initial state (no persistence)

### Requirement: UI store (Zustand)
The system SHALL provide a uiStore (Zustand) for global UI state: theme (light/dark), sidebar state, and toast notifications. Only theme SHALL persist to localStorage.

#### Scenario: Theme toggle
- **WHEN** the user clicks the theme toggle button
- **THEN** uiStore.theme switches between "light" and "dark"

#### Scenario: Theme persists across page reloads
- **WHEN** the user reloads the page
- **THEN** uiStore.theme is restored from localStorage

#### Scenario: Toast notifications
- **WHEN** an action triggers a notification (success, error, warning, info)
- **THEN** a toast object is added to uiStore.toasts array and auto-dismissed after a configurable duration

#### Scenario: Sidebar toggle
- **WHEN** the user clicks the sidebar toggle
- **THEN** uiStore.sidebarOpen is toggled

### Requirement: Global error boundary
The system SHALL provide a React Error Boundary at the layout level to gracefully handle uncaught rendering errors.

#### Scenario: Error boundary catches rendering error
- **WHEN** a component throws an uncaught error during rendering
- **THEN** the error boundary displays a fallback UI with "Something went wrong" message and a "Reload" button

#### Scenario: Error boundary allows recovery
- **WHEN** the user clicks "Reload" on the error boundary fallback
- **THEN** the application resets to the previous route and retries rendering
