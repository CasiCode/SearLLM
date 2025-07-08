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

    def create_query(self, input: InputMessage):
        user = self.db.query(User).get(input.user_id)

        if not user:
            user = User.create(self.db, id=input.user_id)

        query = Query.create(self.db, input.message)

        if user.tokens_used >= user.token_limit:
            raise InsufficientTokensException(
                details=f"User {input.user_id} has reached their token limit."
            )

        user.queries_done += 1
        self.db.refresh(user)

        response = self.handler.process_request(
            input.session_id, input.user_id, input.message
        )

        Response.create(
            self.db,
            query_id=query.id,
            tokens_used=response["tokens_used"],
            text=response["message"],
        )

        self.db.commit()

        return OutputMessage(
            message=response["message"],
            source_documents=response["source_documents"],
            session_id=response["session_id"],
            user_id=response["user_id"],
        )
