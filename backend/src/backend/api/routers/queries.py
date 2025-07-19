"""API Routers processing user queries"""

import logging

from fastapi import Depends, APIRouter

from sqlalchemy.orm import Session

from backend.api.core.structs import InputMessage, OutputMessage
from backend.api.core.request_handler import RequestHandler
from backend.api.services.query_service import QueryService
from backend.api.security.runtime_auth import require_api_token
from backend.database.base import get_db

from backend.agent.graph import process_input_message


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


request_handler = RequestHandler()
request_handler.set_process_function(process_input_message)

router = APIRouter(dependencies=[Depends(require_api_token)])


def get_handler():
    """
    Dependency injection for a RequestHandler
    """
    return request_handler


@router.post("/query", response_model=OutputMessage)
async def ask_question(
    input_message: InputMessage,
    handler: RequestHandler = Depends(get_handler),
    db: Session = Depends(get_db),
):
    """
    Main API router. Creates queries from http requests via QueryService

    Parameters:
        input (InputMessage): InputMessage formatted from the request
    """
    service = QueryService(handler=handler, db=db)

    try:
        response = service.create_query(input_message=input_message)
        return response
    except Exception as e:
        logger.warning("Error while creating a query: %s", e, stacklevel=3)
        return OutputMessage(
            message=f"Error while creating a query: {e}",
            source_documents=[],
            session_id=input_message.session_id,
            user_id=input_message.user_id,
            input_tokens_used=0,
            output_tokens_used=0,
        )


@router.post("/dev", response_model=OutputMessage)
async def response(input_message: InputMessage):
    """
    Development-only API router. Emmits fake responses for incoming queries

    Parameters:
        input (InputMessage): InputMessage formatted from the request
    """

    return OutputMessage(
        message="This is a dev message, yaaaay!",
        source_documents=["https://some-url.com"],
        session_id=input_message.session_id,
        user_id=input_message.user_id,
        input_tokens_used=77,
        output_tokens_used=777,
    )
