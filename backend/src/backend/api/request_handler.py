from typing import Callable, Optional

from backend.api.core.exceptions import ExternalAPIException, LocalAPIException


class RequestHandler:
    def __init__(self):
        self._process_func: Optional[Callable] = None

    def set_process_function(self, func: Callable):
        if not callable(func):
            raise ValueError("Process function must be callable")
        self._process_func = func

    def process_request(self, session_id: str, input_message: str):
        if self._process_func is None:
            raise LocalAPIException(details="No process function registered on server.")

        try:
            # ! response RHS is not correct, no config, no anything
            response = self._process_func(session_id, input_message)
            required_keys = {"answer", "source_documents", "session_id"}
            if not all(key in response for key in required_keys):
                raise ExternalAPIException(details="Bad response format.")
            return response
        except Exception as e:
            raise ExternalAPIException(f"Unexpected error: {str(e)}")
