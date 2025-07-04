from sqlalchemy.orm import Session

from backend.database.models.user import User
from backend.api.core.exceptions import InsufficientTokensException
from backend.api.structs import OutputMessage
from backend.api.request_handler import RequestHandler


# ! CHECK ARGUMENTS LOGIC: I don't think it's right, we're mixing up InputMessage and direct fields
class QueryService:
    def __init__(self, db: Session, handler: RequestHandler):
        self.db = db
        self.handler = handler

    def create_query(self, user_id: int):
        user = self.db.query(User).get(user_id)

        if user.tokens_used >= user.token_limit:
            raise InsufficientTokensException(
                details=f"User {user_id} has reached their token limit."
            )

        response = self.handler.process_request(input.session_id, input.message)
        return OutputMessage(
            message=response["message"],
            source_documents=response["source_documents"],
            session_id=response["session_id"],
            user_id=response["user_id"],
        )
