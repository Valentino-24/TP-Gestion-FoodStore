"""RFC 7807 Problem Details — standardized error responses."""

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ProblemDetail(BaseModel):
    """RFC 7807 problem detail structure."""

    type: str = "about:blank"
    title: str = "Error"
    status: int = 400
    detail: str = ""
    instance: str = ""
    errors: list[dict] = Field(default_factory=list)


def problem_response(
    status_code: int,
    title: str,
    detail: str,
    request: Request | None = None,
    errors: list[dict] | None = None,
    type_url: str | None = None,
) -> JSONResponse:
    """Build an RFC 7807 JSON response."""
    problem = ProblemDetail(
        type=type_url or f"https://httpstatuses.org/{status_code}",
        title=title,
        status=status_code,
        detail=detail,
        instance=str(request.url) if request else "",
        errors=errors or [],
    )
    return JSONResponse(
        status_code=status_code,
        content=problem.model_dump(exclude_none=True),
        headers={"Content-Type": "application/problem+json"},
    )


def register_error_handlers(app):
    """Register RFC 7807 error handlers on the FastAPI app."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for err in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in err.get("loc", [])),
                "message": err.get("msg", "Error de validación"),
            })
        return problem_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Error de validación",
            detail="Uno o más campos no cumplen con las validaciones requeridas.",
            request=request,
            errors=errors,
            type_url="https://httpstatuses.org/422",
        )

    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc: Exception):
        return problem_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            title="Error interno del servidor",
            detail="Ocurrió un error inesperado. Intente nuevamente más tarde.",
            request=request,
            type_url="https://httpstatuses.org/500",
        )

    return app
