from typing import Optional, Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from sqlalchemy.exc import SQLAlchemyError


class APIError(Exception):
    def __init__(
        self,
        status_code: Optional[int] = None,
        details: Optional[str] = None,
        response: Optional[Any] = None,
    ):
        self.status_code = status_code
        self.details = (details,)
        self.response = response

        super().__init__(self.message)


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


class InvalidKeyException(Exception):
    def __init__(self, details: str):
        self.status_code = 401
        self.details = details


async def invalid_key_exception_handler(request: Request, exc: InvalidKeyException):
    return JSONResponse(
        status_code=401,
        content={"message": f"Oops! You used a wrong API KEY... {exc.details or ''}"},
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"message": "Oops! Local database did something..."},
    )


async def insufficient_tokens_handler(
    request: Request, exc: InsufficientTokensException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": f"Oops! Seems like you don't have enough tokens... {exc.details or ''}"
        },
    )


async def local_api_exception_handler(request: Request, exc: LocalAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": f"Oops! Local API did something... {exc.details or ''}"},
    )


async def external_api_exception_handler(request: Request, exc: ExternalAPIException):
    status_code = exc.status_code
    return JSONResponse(
        status_code=status_code,
        content={"message": f"Oops! External API did something... {exc.details or ''}"},
    )


def setup_exception_handlers(app: FastAPI):
    app.add_exception_handler(LocalAPIException, local_api_exception_handler)
    app.add_exception_handler(ExternalAPIException, external_api_exception_handler)
    app.add_exception_handler(InvalidKeyException, invalid_key_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(InsufficientTokensException, insufficient_tokens_handler)
