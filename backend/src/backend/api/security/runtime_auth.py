"""Runtime authentification with API token"""

import os
from typing import Dict, Optional

from dotenv import load_dotenv
from fastapi import Depends
from fastapi.security import APIKeyHeader

from backend.api.core.exceptions import InvalidKeyException
from backend.utils import check_env_variables


load_dotenv()


TOKEN_HEADER_NAME = os.getenv("API_TOKEN_HEADER", "SearLLM-API-token")
token_header = APIKeyHeader(name=TOKEN_HEADER_NAME, auto_error=False)


class RuntimeAuth:
    """Runtime API authentification class. Manages service tokens.

    Methods
    -------
    get_token():
        returns the currently used service token
    verify token(token: Optional[str]):
        verifies if the used token matches with the true one
    """

    def __init__(self):
        check_env_variables("SEARLLM_API_TOKEN")
        self.__token = os.getenv("SEARLLM_API_TOKEN")

    def get_token(self) -> str:
        """Returns the currently used service token"""
        return self.__token

    def verify_token(self, token: Optional[str] = None):
        """Verifies if the used token matches with the true one"""
        if not token or self.__token != token:
            raise InvalidKeyException("Invalid API token used.")
        return token


auth = RuntimeAuth()


def require_api_token(token: str = Depends(token_header)):
    """API token authentificatin dependency for FastAPI"""
    return auth.verify_token(token)


# ? Not sure if this is safe
def get_service_token_header() -> Dict[str, str]:
    """Returns a service token header for HTTP auth"""
    check_env_variables("SEARLLM_API_TOKEN")
    return {TOKEN_HEADER_NAME: os.getenv("SEARLLM_API_TOKEN")}
