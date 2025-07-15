from sqlalchemy.orm import Session

from backend.database.models.user import User
from backend.database.models.query import Query
from backend.database.models.response import Response
from backend.api.core.exceptions import InsufficientTokensException
from backend.api.core.structs import InputMessage, OutputMessage
from backend.api.core.request_handler import RequestHandler


class QueryService:
    def __init__(self, db: Session, handler: RequestHandler):
        self.db = db
        self.handler = handler

    def create_query(self, input_message: InputMessage):
        user = self.db.query(User).get(input_message.user_id)

        if not user:
            user = User.create(self.db, id=input_message.user_id)

        query = Query.create(self.db, input_message.message)

        if user.input_tokens_used >= user.input_token_limit:
            raise InsufficientTokensException(
                details=f"User {input_message.user_id} has reached their input token limit."
            )
        if user.output_tokens_used >= user.output_token_limit:
            raise InsufficientTokensException(
                details=f"User {input_message.user_id} has reached their output token limit."
            )

        response = self.handler.process_request(input_message.message)

        user.queries_done += 1
        user.input_tokens_used += response["input_tokens_used"]
        user.output_tokens_used += response["output_tokens_used"]
        self.db.refresh(user)

        Response.create(
            self.db,
            query_id=query.id,
            text=response["message"],
            input_tokens_used=response["input_tokens_used"],
            output_tokens_used=response["output_tokens_used"],
        )

        self.db.commit()

        return OutputMessage(
            message=response["message"],
            source_documents=response["source_documents"],
            session_id=input_message.session_id,
            input_tokens_used=response["input_tokens_used"],
            output_tokens_used=response["output_tokens_used"],
        )
