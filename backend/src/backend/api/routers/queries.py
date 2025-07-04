from fastapi import Depends, APIRouter

from sqlalchemy.orm import Session

from backend.api.structs import InputMessage, OutputMessage, SourceDocument
from backend.api.request_handler import RequestHandler
from backend.api.services.query_service import QueryService
from backend.api.dependencies import get_db

from backend.agent.graph import process_input_message


request_handler = RequestHandler()
request_handler.set_process_function(process_input_message)

router = APIRouter()


def get_handler():
    return request_handler


@router.post("/query", response_model=OutputMessage)
async def ask_question(
    input: InputMessage,
    handler: RequestHandler = Depends(get_handler),
    db: Session = Depends(get_db),
):
    service = QueryService(handler=handler, db=db)
    return service.create_query(user_id=input["user_id"], query=input["message"])


# ! DEVELOPMENT-ONLY ENDPOINT
@router.post("/dev", response_model=OutputMessage)
async def response(input: InputMessage):
    return OutputMessage(
        message="This is a dev message, yaaaay!",
        source_documents=[
            SourceDocument(source="this is a source", snippet="...some snippet...")
        ],
        session_id=input["session_id"],
        user_id=input["user_id"],
    )
