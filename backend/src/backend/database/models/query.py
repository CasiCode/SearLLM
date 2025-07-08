import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Session

from backend.database.base import Base


class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True, nullable=False, unique=True)
    made_at = Column(DateTime, default=datetime.datetime.now(), nullable=False)

    text = Column(String, default="", nullable=False)

    def __repr__(self):
        return f"<Query(id={self.id}, made_at={self.made_at}, tokens_used={self.tokens_used}, text={self.text})>"

    @classmethod
    def create(
        cls, db: Session, text: str
    ):  # TODO: Calculate optimal ammount, add to config
        new_query = cls(text=text)
        db.add(new_query)
        db.commit()
        db.refresh(new_query)
        return new_query
