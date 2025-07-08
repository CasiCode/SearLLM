# Добавил этот файл только чтобы создать ноду на гите. Можешь свободно его удалять после того, как добавишь в папку что-то еще.

# это pydantic модель выходного сообщения
from backend.api.core.structs import OutputMessage

# чтобы подгрузить конфиг используй эту утилиту
from backend.utils import get_config
# конфигов может быть много по разным путям, но утилита подгружает ЛЮБОЙ
# ты можешь написать и свой yml конфиг для своего модуля

# минимум кода, чтобы получить соответствующий этой модели json ответ от api:
from dotenv import load_dotenv
import os

from backend.api.client import APIClient

load_dotenv()
API_KEY = os.getenv("SEARXTG_API_KEY")

config = get_config("api/config.yml")
api_url = f"{config.api.host}:{str(config.api.port)}"

client = APIClient(base_url=api_url, api_key=API_KEY)

query = {
    "session_id": "abc123",
    "user_id": 123,
    "message": "Какое второе имя у Барака Обамы?",
}


# функция, в которой совершается запрос к API должна быть асинхронной
async def main():
    response_json = await client.post(f"{api_url}/dev", data=query)
    return OutputMessage.model_validate_json(response_json)
