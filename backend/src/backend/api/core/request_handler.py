from typing import Callable, Optional

from langchain_core.runnables import RunnableConfig

from backend.api.core.exceptions import ExternalAPIException, LocalAPIException


class RequestHandler:
    def __init__(self):
        self._process_func: Optional[Callable] = None

    def set_process_function(self, func: Callable):
        if not callable(func):
            raise ValueError("Process function must be callable")
        self._process_func = func

    def process_request(
        self, session_id: str, user_id: int, input_message: str, config: RunnableConfig
    ):
        if self._process_func is None:
            raise LocalAPIException(details="No process function registered on server.")

        try:
            response = self._process_func(session_id, user_id, input_message, config)
            required_keys = {"answer", "source_documents", "session_id"}
            if not all(key in response for key in required_keys):
                raise ExternalAPIException(details="Bad response format.")
            return response
        except Exception as e:
            raise ExternalAPIException(f"Unexpected error: {str(e)}")
