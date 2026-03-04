from fastapi import Request
from fastapi.responses import JSONResponse


class DocForgeError(Exception):
    def __init__(
        self,
        error: str,
        message: str,
        status_code: int = 400,
        details: dict | None = None,
        remediation: str = "",
    ):
        self.error = error
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.remediation = remediation


async def docforge_exception_handler(request: Request, exc: DocForgeError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error,
            "message": exc.message,
            "details": exc.details,
            "remediation": exc.remediation,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": str(exc),
            "details": {},
            "remediation": "An unexpected error occurred. Please try again or contact support.",
        },
    )


def catalog_error(code: str, status_code: int = 400, **kwargs) -> DocForgeError:
    """Create a DocForgeError from the error catalog."""
    from core.error_catalog import get_error

    info = get_error(code, **kwargs)
    return DocForgeError(
        error=code,
        message=info["message"],
        status_code=status_code,
        remediation=info["remediation"],
    )
