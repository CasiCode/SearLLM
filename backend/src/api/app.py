from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from backend.src.agent.graph import process_input_message
from backend.src.api.exceptions import ExternalAPIException, LocalAPIException
from backend.src.api.structs import InputMessage, OutputMessage, SourceDocument
from backend.src.api.request_handler import RequestHandler


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


# ! DEVELOPMENT-ONLY ENDPOINT
@app.post("/dev", response_model=OutputMessage)
async def response(input: InputMessage):
    return OutputMessage(
        message="This is a dev message, yaaaay!",
        source_documents=[
            SourceDocument(source="this is a source", snippet="...some snippet...")
        ],
        session_id=input["session_id"],
    )
