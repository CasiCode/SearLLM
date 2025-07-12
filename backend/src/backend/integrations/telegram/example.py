from backend.api.client import APIClient
from backend.api.core.structs import OutputMessage
from backend.utils import get_config

config = get_config("api/config.yml")
API_URL = f"{config.api.host}:{str(config.api.port)}"

query = {
    "session_id": "abc123",
    "user_id": 123,
    "message": "Какое второе имя у Барака Обамы?",
}


# функция, в которой совершается запрос к API должна быть асинхронной
async def main():
    async with APIClient(base_url=API_URL) as client:
        response_json = await client.post("queries/dev", data=query)
        print(OutputMessage(**response_json))
