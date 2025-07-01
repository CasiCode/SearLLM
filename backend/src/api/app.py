from typing import Callable, Optional

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from backend.src.agent.graph import process_input_message
from backend.src.api.exceptions import ExternalAPIException, LocalAPIException
from backend.src.api.structs import InputMessage, OutputMessage


class RequestHandler:
    def __init__(self):
        self._process_func: Optional[Callable] = None

    def set_process_function(self, func: Callable):
        if not callable(func):
            raise ValueError("Process function must be callable")
        self._process_func = func

    def process_request(self, session_id: str, question: str):
        if self._process_func is None:
            raise LocalAPIException(details="No process function registered on server.")

        try:
            response = self._process_func(session_id, question)
            required_keys = {"answer", "source_documents", "session_id"}
            if not all(key in response for key in required_keys):
                raise ExternalAPIException(details="Bad response format.")
            return response
        except Exception as e:
            raise ExternalAPIException(f"Unexpected error: {str(e)}")


app = FastAPI()
request_handler = RequestHandler()
request_handler.set_process_function(process_input_message)


def get_handler():
    return request_handler


@app.exception_handler(LocalAPIException)
def local_api_exception_handler(request: Request, exc: LocalAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": f"Oops! Local API did something... {exc.details}"},
    )


@app.exception_handler(ExternalAPIException)
def external_api_exception_handler(request: Request, exc: ExternalAPIException):
    status_code = exc.status_code
    return JSONResponse(
        status_code=status_code,
        content={"message": f"Oops! External API did something... {exc.details}"},
    )


@app.post("/query", response_model=OutputMessage)
async def ask_question(
    input: InputMessage, handler: RequestHandler = Depends(get_handler)
):
    response = handler.process_request(input.session_id, input.message)
    return OutputMessage(
        message=response["message"],
        source_documents=response["source_documents"],
        session_id=response["session_id"],
    )
