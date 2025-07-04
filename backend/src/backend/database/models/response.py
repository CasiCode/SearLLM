import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from backend.database.base import Base


class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True, nullable=False, unique=True)
    query_id = Column(
        Integer,
        ForeignKey("queries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    made_at = Column(DateTime, default=datetime.datetime.now(), nullable=False)

    tokens_used = Column(Integer, default=0, nullable=False)
    text = Column(String, default="", nullable=False)

    def __repr__(self):
        return f"<Response(id={self.id}, query_id={self.query_id}, made_at={self.made_at}, tokens_used={self.tokens_used}, text={self.text})>"
