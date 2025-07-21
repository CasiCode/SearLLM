"""
This test ensures that the IP region is as intended.
Useful to check if the proxy is working correctly.
"""

import os
import pprint

import httpx
from dotenv import load_dotenv
from models import Response

load_dotenv()


def clear_json_response(response: dict[str, str]) -> dict[str, str]:
    """Clears json response from garbage using a pydantic model"""
    return Response(**response).model_dump()


def get_base_info():
    """Gets basic regional information for running base"""
    http_client = httpx.Client()

    response = http_client.get("https://ipinfo.io/json")
    return clear_json_response(response.json())


def get_proxy_info():
    """Gets basic regional information for running proxy"""
    http_client = httpx.Client(proxy=os.getenv("SAFE_PROXY_URL"))

    response = http_client.get("https://ipinfo.io/json")
    return clear_json_response(response.json())


if __name__ == "__main__":
    print("Base IP info:")
    pprint.pp(get_base_info())
    print("\nProxy IP info:")
    pprint.pp(get_proxy_info())
