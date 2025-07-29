"""A model for user queries"""

import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Session

from backend.database.base import Base


class Query(Base):
    """
    Anonimized Query database model.

    Attributes
    ----------
    id : Integer
        id primary key, indexed in the table, not nullable and unique
    made_at : DateTime
        date and time of the query, defaults to current UTC datetime, not nullable
    text : String
        full text of the query
    """

    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True, nullable=False, unique=True)
    made_at = Column(
        DateTime, default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )

    text = Column(String, default="", nullable=False)

    def __repr__(self):
        return f"<Query(id={self.id}, made_at={self.made_at}, text={self.text})>"

    @classmethod
    def create(cls, db: Session, text: str):
        """A Query model factory"""
        new_query = cls(text=text)
        db.add(new_query)
        db.commit()
        db.refresh(new_query)
        return new_query
