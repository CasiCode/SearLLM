import logging

from fastapi import Depends, APIRouter

from sqlalchemy.orm import Session

from backend.api.core.structs import InputMessage, OutputMessage, SourceDocument
from backend.api.core.request_handler import RequestHandler
from backend.api.core.exceptions import InsufficientTokensException
from backend.api.services.query_service import QueryService
from backend.api.security.runtime_auth import require_api_token
from backend.database.base import get_db

from backend.agent.graph import process_input_message


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


request_handler = RequestHandler()
request_handler.set_process_function(process_input_message)

router = APIRouter(dependencies=[Depends(require_api_token)])


def get_handler():
    return request_handler


@router.post("/query", response_model=OutputMessage)
async def ask_question(
    input: InputMessage,
    handler: RequestHandler = Depends(get_handler),
    db: Session = Depends(get_db),
):
    service = QueryService(handler=handler, db=db)

    try:
        return service.create_query(user_id=input["user_id"], query=input["message"])
    except InsufficientTokensException as e:
        logger.warning(f"Error while creating a query: {e.details}", stacklevel=3)
        return None


# ! DEVELOPMENT-ONLY ENDPOINT
@router.post("/dev", response_model=OutputMessage)
async def response(input: InputMessage):
    return OutputMessage(
        message="This is a dev message, yaaaay!",
        source_documents=[
            SourceDocument(source="this is a source", snippet="...some snippet...")
        ],
        session_id=input.session_id,
        user_id=input.user_id,
        input_tokens_used=77,
        output_tokens_used=777,
    )
