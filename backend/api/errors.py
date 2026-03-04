from fastapi import Request
from fastapi.responses import JSONResponse


class DocForgeError(Exception):
    def __init__(
        self, error: str, message: str, status_code: int = 400, details: dict | None = None
    ):
        self.error = error
        self.message = message
        self.status_code = status_code
        self.details = details or {}


async def docforge_exception_handler(request: Request, exc: DocForgeError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error, "message": exc.message, "details": exc.details},
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "message": str(exc), "details": {}},
    )
