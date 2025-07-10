from fastapi import Request
from fastapi.security import APIKeyHeader

from backend.api.core.exceptions import InvalidKeyException
from backend.security.utils import generate_service_key


class LocalAuth:
    def __init__(self):
        self.token = generate_service_key(prefix="st")
        self.header_name = APIKeyHeader(name="SearXTG-API-token")

    def verify_token(self, request: Request):
        request_token = request.headers.get(self.header_name)
        if not request_token or self.token != request_token:
            raise InvalidKeyException("Invalid API token used.")
        return True
