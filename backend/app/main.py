"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import engine, Base
from app.core.error_handling import register_error_handlers


# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup: Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: Dispose engine
    await engine.dispose()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Add rate limiter
    app.state.limiter = limiter

    # Register RFC 7807 error handlers
    register_error_handlers(app)

    # Exception handler for rate limiting
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests"}
        )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    # Register routers
    from app.auth.router import router as auth_router
    from app.categorias.router import router as categorias_router
    from app.clientes.router import router as clientes_router
    from app.productos.router import router as productos_router
    from app.refreshtokens.router import router as refreshtokens_router
    from app.direcciones.router import router as direcciones_router
    from app.pedidos.router import router as pedidos_router
    from app.pagos.router import router as pagos_router
    from app.admin.router import router as admin_router
    from app.cocina.router import router as cocina_router

    app.include_router(auth_router, prefix=settings.API_PREFIX)
    app.include_router(categorias_router, prefix=settings.API_PREFIX)
    app.include_router(clientes_router, prefix=settings.API_PREFIX)
    app.include_router(productos_router, prefix=settings.API_PREFIX)
    app.include_router(refreshtokens_router, prefix=settings.API_PREFIX)
    app.include_router(direcciones_router, prefix=settings.API_PREFIX)
    app.include_router(pedidos_router, prefix=settings.API_PREFIX)
    app.include_router(pagos_router, prefix=settings.API_PREFIX)
    app.include_router(admin_router, prefix=settings.API_PREFIX)
    app.include_router(cocina_router, prefix=settings.API_PREFIX)

    return app


app = create_app()