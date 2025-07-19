"""Exceptions and exception handlers specific to the API"""

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
        self.details = details
        self.response = response


class BaseAPIException(Exception):
    def __repr__(self):
        return f"<{self.__class__.__name__}(status_code={self.status_code}, details={self.details})>"

    def __str__(self):
        return f"<{self.__class__.__name__}(status_code={self.status_code}, details={self.details})>"


class LocalAPIException(BaseAPIException):
    """General local API exception"""

    def __init__(self, details: str):
        self.status_code = 503
        self.details = details


class ExternalAPIException(BaseAPIException):
    """General external API exception"""

    def __init__(self, details: str):
        self.status_code = 421
        self.details = details


class InsufficientTokensException(LocalAPIException):
    """Intended to be raised when there's not enough tokens to perform a query"""

    def __init__(self, details: str):
        self.status_code = 403
        self.details = details


class InvalidKeyException(LocalAPIException):
    """Intended to be raised when API tokens don't match"""

    def __init__(self, details: str):
        self.status_code = 401
        self.details = details


async def invalid_key_exception_handler(request: Request, exc: InvalidKeyException):
    """FastAPI exception handler for InvalidKeyException"""
    # pylint: disable=unused-argument
    return JSONResponse(
        status_code=401,
        content={"message": f"Oops! You used a wrong API KEY... {exc.details or ''}"},
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """FastAPI exception handler for SQLAlchemyError"""
    # pylint: disable=unused-argument
    return JSONResponse(
        status_code=500,
        content={"message": "Oops! Local database did something..."},
    )


async def insufficient_tokens_handler(
    request: Request, exc: InsufficientTokensException
):
    """FastAPI exception handler for InsufficientTokensException"""
    # pylint: disable=unused-argument
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": f"Oops! Seems like you don't have enough tokens... {exc.details or ''}"
        },
    )


async def local_api_exception_handler(request: Request, exc: LocalAPIException):
    """FastAPI exception handler for LocalAPIException"""
    # pylint: disable=unused-argument
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": f"Oops! Local API did something... {exc.details or ''}"},
    )


async def external_api_exception_handler(request: Request, exc: ExternalAPIException):
    """FastAPI exception handler for ExternalAPIException"""
    # pylint: disable=unused-argument
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
