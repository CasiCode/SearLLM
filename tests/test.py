import asyncio
import os
import pprint
import uuid

from dotenv import load_dotenv

from backend.api.client import APIClient
from backend.utils import get_config, check_env_variables

load_dotenv()
check_env_variables("SEARXTG_API_TOKEN")
API_KEY = os.getenv("SEARXTG_API_TOKEN")

config = get_config("api/config.yml")
api_url = f"{config.api.host}:{str(config.api.port)}"

query = {
    "session_id": str(uuid.uuid4()),
    "user_id": 12372396423847234,
    "message": "How many awards did Michael Jackson win throughout his entire carrer?",
}


async def main():
    async with APIClient(base_url=api_url) as client:
        response_json = await asyncio.wait_for(
            client.post("queries/query", data=query), timeout=60
        )
        pprint.pp(response_json)


if __name__ == "__main__":
    asyncio.run(main())
