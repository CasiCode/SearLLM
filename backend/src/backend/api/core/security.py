import os

from fastapi import Security
from fastapi.security import APIKeyHeader

from backend.api.core.exceptions import InvalidKeyException


SERVICE_API_KEY = os.getenv("SERVICE_API_KEY")
api_key_header = APIKeyHeader(name="SearXTG-API-key")


async def verify_service_key(api_key: str = Security(api_key_header)) -> bool:
    if api_key != SERVICE_API_KEY:
        raise InvalidKeyException("Invalid SERVICE_API_KEY used.")
    return True
