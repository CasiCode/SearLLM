# Добавил этот файл только чтобы создать ноду на гите. Можешь свободно его удалять после того, как добавишь в папку что-то еще.

# это pydantic модель выходного сообщения
from src.api.structs import OutputMessage

# минимум кода, чтобы получить соответствующий этой модели json ответ от api:
import requests

query = {
    "session_id": "abc123",
    "message": "Какое второе имя у Барака Обамы?",
}

API_URL = "127.0.0.0:8888"
response_json = requests.post(f"{API_URL}/query", json=query)
response = OutputMessage.model_validate_json(response_json)
