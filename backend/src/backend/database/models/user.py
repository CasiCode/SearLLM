from sqlalchemy import Column, Integer

from backend.database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, nullable=False, unique=True)
    tokens_used = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, tokens_used={self.tokens_used})>"
