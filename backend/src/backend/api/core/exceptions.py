from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from sqlalchemy.exc import SQLAlchemyError


class LocalAPIException(Exception):
    def __init__(self, details: str):
        self.status_code = 503
        self.details = details


class ExternalAPIException(Exception):
    def __init__(self, details: str):
        self.status_code = 421
        self.details = details


class InsufficientTokensException(Exception):
    def __init__(self, details: str):
        self.status_code = 403
        self.details = details


async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"message": "Oops! Local database did something..."},
    )


async def insufficient_tokens_error(request: Request, exc: InsufficientTokensException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": f"Oops! Seems like you don't have enough tokens... {exc.details}"
        },
    )


async def local_api_exception_handler(request: Request, exc: LocalAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": f"Oops! Local API did something... {exc.details}"},
    )


async def external_api_exception_handler(request: Request, exc: ExternalAPIException):
    status_code = exc.status_code
    return JSONResponse(
        status_code=status_code,
        content={"message": f"Oops! External API did something... {exc.details}"},
    )


def setup_exception_handlers(app: FastAPI):
    app.add_exception_handler(LocalAPIException, local_api_exception_handler)
    app.add_exception_handler(ExternalAPIException, external_api_exception_handler)
