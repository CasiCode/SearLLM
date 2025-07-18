"""A model for user queries"""

import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Session

from backend.database.base import Base


class Query(Base):
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
        new_query = cls(text=text)
        db.add(new_query)
        db.commit()
        db.refresh(new_query)
        return new_query
