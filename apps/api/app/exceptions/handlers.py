from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.exceptions.exceptions import APIException


async def core_api_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, APIException):
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.message}
        )
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


async def integrity_error_handler(_: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=409,
            content={"detail": "An unexpected error has occurred, please try again."},
        )
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(APIException, core_api_exception_handler)
