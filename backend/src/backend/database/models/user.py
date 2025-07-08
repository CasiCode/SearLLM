from sqlalchemy import Column, Integer
from sqlalchemy.orm import Session

from backend.database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, nullable=False, unique=True)
    queries_done = Column(Integer, default=0, nullable=False)
    tokens_used = Column(Integer, default=0, nullable=False)
    token_limit = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, queries_done={self.queries_done}, tokens_used={self.tokens_used}), token_limit={self.token_limit}>"

    @classmethod
    def create(
        cls, db: Session, id: int, token_limit: int = 10000
    ):  # TODO: Calculate optimal ammount, add to config
        new_user = cls(id=id, token_limit=token_limit)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
