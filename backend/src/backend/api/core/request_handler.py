"""Manages API requests and transmits them to the Langgraph layer"""

from typing import Callable, Optional

from langchain_core.runnables import RunnableConfig

from backend.api.core.exceptions import ExternalAPIException, LocalAPIException


class RequestHandler:
    """RequestHandler

    Methods
    -------
    __init__(self):
        Constructor
    set_process_function(func: Callable):
        Sets self._process_func to func.
    process_request(session_id: str, user_id: int, input_message: str, config: RunnableConfig):
        Processes incoming request and tries to run self._process_func on its data
    """

    def __init__(self):
        """
        Constructor
        """

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

    def process_request(
        self, session_id: str, user_id: int, input_message: str, config: RunnableConfig
    ):
        """
        Processes incoming request and tries to run self._process_func on its data

        Parameters:
            session_id (str): Request session id
            user_id (int): id of the user who issued the request
            input_message (str): user message to be processed with langgraph
            config (RunnableConfig): langgraph config
        """

        if self._process_func is None:
            raise LocalAPIException(details="No process function registered on server.")

        try:
            response = self._process_func(session_id, user_id, input_message, config)
            required_keys = {"answer", "source_documents", "session_id"}
            if not all(key in response for key in required_keys):
                raise ExternalAPIException(details="Bad response format.")
            return response
        except Exception as e:
            raise ExternalAPIException(f"Unexpected error: {str(e)}") from e
