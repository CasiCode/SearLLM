"""A model for API responses"""

import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Session

from backend.database.base import Base


class Response(Base):
    """
    Anonimized Response database model.

    Attributes
    ----------
    id : Integer
        id primary key, indexed in the table, not nullable and unique
    query_id : Integer
        Foreign key linking to a Query entry, not nullable, indexed in the table
    made_at : DateTime
        date and time of the response, defaults to current UTC datetime, not nullable
    input_tokens_used : Integer
        numeber of input token used in response generation
    output_tokens_used : Integer
        numeber of output token used in response generation
    text : String
        full text of the response
    """

    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True, nullable=False, unique=True)
    query_id = Column(
        Integer,
        ForeignKey("queries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    made_at = Column(
        DateTime, default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )

    input_tokens_used = Column(Integer, default=0, nullable=False)
    output_tokens_used = Column(Integer, default=0, nullable=False)
    text = Column(String, default="", nullable=False)

    def __repr__(self):
        return (
            f"<Response(id={self.id}, query_id={self.query_id}, "
            f"made_at={self.made_at}, input_tokens_used={self.input_tokens_used}, "
            f"output_tokens_used={self.output_tokens_used}, text={self.text})>"
        )

    @classmethod  # pylint: disable=too-many-arguments, too-many-positional-arguments
    def create(
        cls,
        db: Session,
        query_id: int,
        input_tokens_used: int,
        output_tokens_used: int,
        text: str,
    ):
        """A Response model factory"""
        new_response = cls(
            query_id=query_id,
            input_tokens_used=input_tokens_used,
            output_tokens_used=output_tokens_used,
            text=text,
        )
        db.add(new_response)
        db.commit()
        db.refresh(new_response)
        return new_response
