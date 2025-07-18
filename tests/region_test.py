"""
This test ensures that the IP region is as intended.
Useful to check if the proxy is working correctly.
"""

import os
import pprint

import httpx
from dotenv import load_dotenv

load_dotenv()


def get_base_info():
    """Gets basic regional information for running base"""
    http_client = httpx.Client()

    response = http_client.get("https://ipinfo.io/json")
    return response.json()


def get_proxy_info():
    """Gets basic regional information for running proxy"""
    print(os.getenv("PROXY_URL"))

    http_client = httpx.Client(proxy=os.getenv("PROXY_URL"))

    response = http_client.get("https://ipinfo.io/json")
    return response.json()


if __name__ == "__main__":
    print("Base IP info:")
    pprint.pp(get_base_info())
    print("\nProxy IP info:")
    pprint.pp(get_proxy_info())
