from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.schemas import fail


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content=fail(str(exc.status_code), exc.detail).model_dump())


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = {"errors": exc.errors()}
    return JSONResponse(status_code=422, content=fail("ValidationError", "Request validation failed", details).model_dump())


async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content=fail("InternalServerError", "Unexpected error").model_dump())
