# Добавил этот файл только чтобы создать ноду на гите. Можешь свободно его удалять после того, как добавишь в папку что-то еще.

# это pydantic модель выходного сообщения
from src.api.structs import OutputMessage

# минимум кода, чтобы получить соответствующий этой модели json ответ от api:
import requests

query = {
    "session_id": "abc123",
    "message": "В каких областях Neoflex обладает экспертизой?",
}
response_json = requests.post("api-url/query", json=query)
response = OutputMessage.model_validate_json(response_json)

# можно пробовать получать ответ не через API, а напрямую от langgraph, но мне нужно подумать над тем, насколько это резонно
