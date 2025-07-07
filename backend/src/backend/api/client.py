import datetime
import json
import logging
from typing import Dict, Optional

from aiohttp import ClientSession, ClientTimeout, ClientError

from backend.api.core.exceptions import APIError

logger = logging.getLogger(__name__)


class APIClient:
    def __init__(self, base_url: str, api_key: str, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = ClientTimeout(total=timeout)
        self.session = Optional[ClientSession] = None

        self.headers = {
            "SearXTG-API-key": self.api_key,
            "Content-Type": "application/json",
        }

    async def create_session(self):
        if self.session is None:
            self.session = ClientSession(headers=self.headers, timeout=self.timeout)

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def __aenter__(self):
        await self.create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # ? Args not used
        await self.close_session()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        payload: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ):
        if self.session is None:
            await self.create_session()

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        start_time = datetime.datetime.now()

        try:
            async with self.session.request(
                method=method,
                url=url,
                json=payload,
                params=params,
            ) as response:
                logger.debug(
                    "API Request",
                    extra={
                        "method": method,
                        "url": url,
                        "status_code": response.status,
                        "duration": (
                            datetime.datetime.now() - start_time
                        ).total_seconds(),
                        "payload_size": len(json.dumps(payload)) if payload else 0,
                    },
                )

                response.raise_for_status()

                return await response.json()

        except ClientError as e:
            logger.error(
                "API Request Failed",
                extra={
                    "method": method,
                    "url": url,
                    "error": str(e),
                    "duration": (datetime.datetime.now() - start_time).total_seconds(),
                },
            )

            raise APIError(
                status_code=getattr(e.response, "status_code", None),
                details=f"Oops! Request failed: {e}",
                response=getattr(e, "response", None),
            )

    async def post(self, endpoint: str, data: Dict) -> Dict:
        return await self._make_request(method="POST", endpoint=endpoint, payload=data)

    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        return await self._make_request(method="GET", endpoint=endpoint, params=params)
