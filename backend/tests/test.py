"""Tests running API by posting a query on its endpoint"""

import asyncio
import os
import pprint
import uuid

from dotenv import load_dotenv

from backend.api.client import APIClient
from backend.utils import get_config, check_env_variables

load_dotenv()
check_env_variables("SEARLLM_API_TOKEN")
API_KEY = os.getenv("SEARLLM_API_TOKEN")

config = get_config("api/config.yml")
API_URL = f"{config.api.host}:{str(config.api.port)}"

query = {
    "session_id": str(uuid.uuid4()),
    "user_id": 1234567890123,
    "message": "How many awards did Michael Jackson win throughout his entire carrer?",
}


async def main():
    async with APIClient(base_url=API_URL) as client:
        response_json = await asyncio.wait_for(
            client.post("queries/query", data=query), timeout=60
        )
        pprint.pp(response_json)


if __name__ == "__main__":
    asyncio.run(main())
