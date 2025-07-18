"""Runtime authentification with API token"""

import os
from typing import Optional, Dict

from dotenv import load_dotenv
from fastapi import Depends
from fastapi.security import APIKeyHeader

from backend.api.core.exceptions import InvalidKeyException

load_dotenv()


TOKEN_HEADER_NAME = os.getenv("API_TOKEN_HEADER", "SearXTG-API-token")
token_header = APIKeyHeader(name=TOKEN_HEADER_NAME, auto_error=False)


class RuntimeAuth:
    def __init__(self):
        self.__token = os.getenv("SEARXTG_API_TOKEN")

    def get_token(self) -> str:
        return self.__token

    def verify_token(self, token: Optional[str] = None):
        if not token or self.__token != token:
            raise InvalidKeyException("Invalid API token used.")
        return token


auth = RuntimeAuth()


def require_api_token(token: str = Depends(token_header)):
    return auth.verify_token(token)


def get_service_token_header() -> Dict[str, str]:
    return {TOKEN_HEADER_NAME: os.getenv("SEARXTG_API_TOKEN")}
