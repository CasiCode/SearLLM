import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from backend.database.base import Base


class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True, nullable=False, unique=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    made_at = Column(DateTime, default=datetime.datetime.now(), nullable=False)

    tokens_used = Column(Integer, default=0, nullable=False)
    text = Column(String, default="", nullable=False)

    def __repr__(self):
        return f"<Query(id={self.id}, user_id={self.user_id}, made_at={self.made_at}, tokens_used={self.tokens_used}, text={self.text})>"
