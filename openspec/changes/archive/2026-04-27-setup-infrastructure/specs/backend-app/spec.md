## ADDED Requirements

### Requirement: FastAPI application entry point
The application SHALL provide a FastAPI entry point in `backend/app/main.py` with proper middleware configuration.

#### Scenario: App starts successfully
- **WHEN** developer runs `uvicorn app.main:app --reload`
- **THEN** FastAPI server starts on port 8000 with /docs and /redoc endpoints

#### Scenario: CORS configured
- **WHEN** frontend makes request from `http://localhost:5173`
- **THEN** CORS allows the request without blocking

#### Scenario: Rate limiting applied
- **WHEN** client makes 100+ requests per minute to /auth/login
- **THEN** HTTP 429 returned after 5 attempts per 15 minutes

### Requirement: Environment configuration
The application SHALL load configuration from environment variables using Pydantic Settings.

#### Scenario: Config loads from .env
- **WHEN** application starts
- **THEN** reads DATABASE_URL, SECRET_KEY, CORS_ORIGINS from .env

#### Scenario: Missing required config fails startup
- **WHEN** DATABASE_URL not set in environment
- **THEN** application fails to start with clear error message