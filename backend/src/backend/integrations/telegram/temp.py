# Добавил этот файл только чтобы создать ноду на гите. Можешь свободно его удалять после того, как добавишь в папку что-то еще.

# это pydantic модель выходного сообщения
from backend.src.backend.api.structs import OutputMessage

# чтобы подгрузить конфиг
from backend.src.backend.utils import get_config

config = get_config("../../api/config.yml")

# конфигов может быть много по разным путям, но утилита подгружает ЛЮБОЙ
# ты можешь написать и свой yml конфиг для своего модуля

# минимум кода, чтобы получить соответствующий этой модели json ответ от api:
import requests

query = {
    "session_id": "abc123",
    "message": "Какое второе имя у Барака Обамы?",
}

api_url = f"{config.host}:{str(config.port)}"
response_json = requests.post(f"{api_url}/dev", json=query)
response = OutputMessage.model_validate_json(response_json)
