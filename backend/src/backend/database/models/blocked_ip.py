import datetime

from sqlalchemy import Column, Integer, String, DateTime

from backend.database.base import Base


class BlockedIP(Base):
    __tablename__ = "blocked_ips"

    id = Column(Integer, primary_key=True, index=True, nullable=False, unique=True)
    ip_address = Column(String, index=True, nullable=False)

    blocked_until = Column(DateTime, nullable=False)
    failed_attemps = Column(Integer, default=0, nullable=False)
    first_attempt = Column(DateTime, default=datetime.datetime.now())
    last_attempt = Column(DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return f"<Query(id={self.id}, user_id={self.user_id}, made_at={self.made_at}, tokens_used={self.tokens_used}, text={self.text})>"
