## ADDED Requirements

### Requirement: Project scaffolding
The system SHALL provide a Vite + React + TypeScript project with TailwindCSS v4 configured and all base dependencies installed.

#### Scenario: Project builds successfully
- **WHEN** the project is scaffolded with `npm create vite@latest` using React + TypeScript template
- **THEN** `npm run build` produces a production build without errors

#### Scenario: TailwindCSS is configured
- **WHEN** the project starts in dev mode
- **THEN** TailwindCSS utility classes SHALL be applied correctly in the browser

### Requirement: Routing structure
The system SHALL implement react-router-dom with three route groups: public routes (no auth required), authenticated routes (token required), and admin routes (ADMIN role required).

#### Scenario: Public routes are accessible without auth
- **WHEN** an unauthenticated user navigates to /login or /register
- **THEN** the page renders without redirect

#### Scenario: Authenticated routes redirect to login
- **WHEN** an unauthenticated user navigates to a protected route (e.g. /productos)
- **THEN** the system redirects to /login

#### Scenario: Admin routes require ADMIN role
- **WHEN** a non-ADMIN authenticated user navigates to /admin/*
- **THEN** the system redirects to /

#### Scenario: Admin routes are accessible by ADMIN
- **WHEN** an authenticated user with ADMIN role navigates to /admin/*
- **THEN** the admin layout renders correctly

### Requirement: Base layout components
The system SHALL provide reusable layout components: a public Layout (centered, minimal), an authenticated Layout (with navbar and sidebar area), and an admin Layout (with admin-specific navigation).

#### Scenario: Public layout renders login/register
- **WHEN** a user visits /login
- **THEN** the page renders with a centered card layout without navbar or sidebar

#### Scenario: Authenticated layout shows navbar
- **WHEN** an authenticated user visits any protected route
- **THEN** the page renders with a top navbar showing user name and logout button

#### Scenario: Admin layout shows admin navigation
- **WHEN** an ADMIN user visits /admin
- **THEN** the page renders with admin-specific sidebar navigation

### Requirement: Environment configuration
The system SHALL load API base URL from environment variables via Vite's `import.meta.env`.

#### Scenario: API URL is configurable
- **WHEN** the app starts
- **THEN** it reads `VITE_API_URL` from environment variables (default: `http://localhost:8000/api/v1`)

#### Scenario: Dev server uses correct port
- **WHEN** the dev server starts
- **THEN** it runs on port 5173 (configurable via `vite.config.ts`)
