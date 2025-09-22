"""A model for user queries"""

import datetime

from sqlalchemy import Column, Date, Integer
from sqlalchemy.orm import Session

from backend.database.base import Base


class ActivityInfo(Base):
    """
    Basic daily activity for an API.

    Attributes
    ----------
    id : Integer
        id primary key, indexed in the table, not nullable and unique
    date : DateTime
        date of the reported activity, defaults to current local date, not nullable
    requests : int
        total amount of requests made this day
    shares : int
        total amount of shares done this day
    """

    __tablename__ = "activity_info"

    id = Column(Integer, primary_key=True, index=True, nullable=False, unique=True)
    date = Column(Date, default=datetime.date.today(), nullable=False)
    requests = Column(Integer, default=0, nullable=False)
    shares = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        return (
            f"<ActivityInfo(id={self.id}, date={self.date}, "
            f"requests={self.requests}, shares={self.shares})>"
        )

    @classmethod
    def create(cls, db: Session):
        """An ActivityInfo model factory"""
        new_info = cls()
        db.add(new_info)
        db.commit()
        db.refresh(new_info)
        return new_info
