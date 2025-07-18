"""Manages API requests and transmits them to the Langgraph layer"""

from typing import Callable, Optional

from backend.api.core.exceptions import ExternalAPIException, LocalAPIException
from backend.api.core.structs import InputMessage


class RequestHandler:
    """Handles API requests and transmits them to Langgraph

    Methods
    -------
    set_process_function(func: Callable):
        Sets self._process_func to func.
    process_request(session_id: str, user_id: int, input_message: str, config: RunnableConfig):
        Processes incoming request and tries to run self._process_func on its data
    """

    def __init__(self):
        self._process_func: Optional[Callable] = None

    def set_process_function(self, func: Callable):
        """
        Sets self._process_func to func.

        Parameters:
            func (Callable): function to be set as a request processor
        """

        if not callable(func):
            raise ValueError("Process function must be callable")
        self._process_func = func

    def process_request(self, input_message: InputMessage):
        """
        Processes incoming request and tries to run self._process_func on its data

        Parameters:
            input_message (InputMessage): user message to be processed with langgraph
        """

        if self._process_func is None:
            raise LocalAPIException(details="No process function registered on server.")

        try:
            return self._process_func(input_message)
        except Exception as e:
            raise ExternalAPIException(
                f"Unexpected error: {type(e).__name__} - {str(e)}"
            ) from e
