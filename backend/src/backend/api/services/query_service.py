"""Query manager. Creates, sends and adds to DB both the requests and the responses to the API"""

from datetime import date

from sqlalchemy.orm import Session

from backend.api.core.exceptions import InsufficientTokensException
from backend.api.core.request_handler import RequestHandler
from backend.api.core.structs import InputMessage, OutputMessage
from backend.database.models.query import Query
from backend.database.models.activity_info import ActivityInfo
from backend.database.models.response import Response
from backend.database.models.user import User
from backend.utils import get_logger


logger = get_logger(name=__name__)


class QueryService:
    """Query Service managing incoming user queries caught by the API

    Attributes
    ----------
    db : sqlalchemy.orm.Session
        The session that will store both user data
        and the request-response entries
    handler : RequestHandler
        A request handler that will process the incoming requets
    save_data: bool
        A flag indicating if the service should save
        the requests and responses to the DB

    Methods
    -------
    create_query(input_message: InputMessage):
        Creates and manages a query accordingly to given InputMessage
    """

    def __init__(self, db: Session, handler: RequestHandler, save_data: bool = False):
        self.db = db
        self.handler = handler
        self.save_data = save_data

    async def create_query(self, input_message: InputMessage):
        user = self.db.query(User).get(input_message.user_id)

        if not user:
            user = User.create(self.db, id=input_message.user_id)

        if user.input_tokens_used >= user.input_token_limit:
            raise InsufficientTokensException(
                details=f"User {input_message.user_id} has reached their input token limit."
            )
        if user.output_tokens_used >= user.output_token_limit:
            raise InsufficientTokensException(
                details=f"User {input_message.user_id} has reached their output token limit."
            )

        response = await self.handler.process_request(
            input_message=input_message.message, language=input_message.pref_language
        )

        user.queries_done += 1
        user.input_tokens_used += response["input_tokens_used"]
        user.output_tokens_used += response["output_tokens_used"]

        if self.save_data:
            query = Query.create(self.db, input_message.message)
            Response.create(
                self.db,
                query_id=query.id,
                text=response["message"],
                input_tokens_used=response["input_tokens_used"],
                output_tokens_used=response["output_tokens_used"],
            )

        activity = (
            self.db.query(ActivityInfo)
            .filter(ActivityInfo.date == date.today())
            .first()
        )
        if not activity:
            activity = ActivityInfo.create(self.db)
        activity.requests += 1

        self.db.commit()
        logger.info("Updating user entry:\n%s", user)

        return OutputMessage(
            message=response["message"],
            highlight=response["highlight"],
            source_documents=response["source_documents"],
            session_id=input_message.session_id,
            input_tokens_used=response["input_tokens_used"],
            output_tokens_used=response["output_tokens_used"],
        )
