"""Asyncronous API Client logic"""

import datetime
import json
import logging
from typing import Dict, Optional

from aiohttp import ClientSession, ClientTimeout, ClientError

from backend.api.core.exceptions import APIError
from backend.api.security.runtime_auth import get_service_token_header

logger = logging.getLogger(__name__)


class APIClient:
    """API Client managing asyncronous http requests to routers

    Attributes
    ----------
    base_url : str
        Base API URL, should be set to the URL of API host
    timeout : ClientTimeout
        Timeout to be used when making requests
    Session : Optional[ClientSession]
        Async HTTP Session to be used by the Client

    Methods
    -------
    create_session():
        Explicitly creates a session for Client
    close_session():
        Explicitly closes a session
    post(endpoint: str, data: Dict):
        Makes a POST http request
    get(endpoint: str, params: Optional[Dict] = None):
        Makes a GET http request

    """

    def __init__(self, base_url: str, timeout: int = 25):
        self.base_url = base_url.rstrip("/")
        self.timeout = ClientTimeout(total=timeout)
        self.session: Optional[ClientSession] = None

        self.headers = {
            "Content-Type": "application/json",
        }
        self.headers.update(get_service_token_header())

    async def create_session(self):
        """Explicitly creates a session for Client"""
        if self.session is None:
            self.session = ClientSession(headers=self.headers, timeout=self.timeout)

    async def close_session(self):
        """Explicitly closes a session for Client"""
        if self.session:
            await self.session.close()
            self.session = None

    async def __aenter__(self):
        """Creates a session for Client in context manager"""
        await self.create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # ? Args not used
        """Closes a session for Client in context manager"""
        await self.close_session()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        payload: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ):
        """
        Makes a request to the API server

        Parameters:
            method (str): HTTP request method
            endpoint (str): API endpoint to make a request on
            payload (Optional[Dict]): Request data
            params (Optional[Dict]): Additional parameters
        """
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
                headers=self.headers,
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
                status_code=getattr(e.response, "status_code", None)
                if hasattr(e, "response")
                else None,
                details=f"Oops! Request failed: {e}",
                response=getattr(e, "response", None),
            ) from e

    async def post(self, endpoint: str, data: Dict) -> Dict:
        """
        Makes a POST request to the API server at base_url/endpoint

        Parameters:
            endpoint (str): API endpoint to make a request on
            data (Dict): Request data
        """
        return await self._make_request(method="POST", endpoint=endpoint, payload=data)

    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Makes a GET request to the API server at base_url/endpoint

        Parameters:
            endpoint (str): API endpoint to make a request on
            params (Dict): GET parameters
        """
        return await self._make_request(method="GET", endpoint=endpoint, params=params)
