"""A model for users"""

from sqlalchemy import Column, Integer
from sqlalchemy.orm import Session

from backend.database.base import Base
from backend.utils import get_config


config = get_config("database/config.yml")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, nullable=False, unique=True)
    queries_done = Column(Integer, default=0, nullable=False)
    input_tokens_used = Column(Integer, default=0, nullable=False)
    output_tokens_used = Column(Integer, default=0, nullable=False)
    input_token_limit = Column(Integer, default=0, nullable=False)
    output_token_limit = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        return (
            f"<User(id={self.id}, queries_done={self.queries_done}, "
            f"input_tokens_used={self.input_tokens_used}, "
            f"output_tokens_used={self.output_tokens_used}, "
            f"input_token_limit={self.input_token_limit}, "
            f"output_token_limit={self.output_token_limit}>"
        )

    @classmethod  # pylint: disable=too-many-arguments, too-many-positional-arguments
    def create(
        cls,
        db: Session,
        id: int,
        input_tokens_used: int = 0,
        output_tokens_used=0,
        input_token_limit: int = config.user.input_token_limit,
        output_token_limit: int = config.user.output_token_limit,
    ):
        new_user = cls(
            id=id,
            input_tokens_used=input_tokens_used,
            output_tokens_used=output_tokens_used,
            input_token_limit=input_token_limit,
            output_token_limit=output_token_limit,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
