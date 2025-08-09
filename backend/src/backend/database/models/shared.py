"""A model for Shared Searches"""

from typing import List
import secrets
import base64

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

from backend.database.base import Base


class SharedSearch(Base):
    """
    Shared search database model.

    Attributes
    ----------
    id : Integer
        id primary key, indexed in the table, not nullable and unique
    slug : String
        unique random string used as part of sharing link
    query : String
        text of the query
    highlight : String
        highlight of the response
    text : String
        full text of the response
    source_documents : ARRAY(String)
        list of sources
    """

    __tablename__ = "shared_responses"

    id = Column(Integer, primary_key=True, index=True, nullable=False, unique=True)
    slug = Column(String, default="", nullable=False, index=True, unique=True)
    query = Column(String, default="", nullable=False)
    highlight = Column(String, default="", nullable=False)
    text = Column(String, default="", nullable=False)
    source_documents = Column(String, default="", nullable=False)

    def __repr__(self):
        return (
            f"<SharedSearch(id={self.id}, slug={self.slug}, "
            f"query={self.query}, highlight={self.highlight}, "
            f"text={self.text}, source_documents={self.source_documents})>"
        )

    @staticmethod
    def generate_slug(length: int = 32):
        random_bytes = secrets.token_bytes(length)
        slug = base64.urlsafe_b64encode(random_bytes).decode("utf-8")
        slug = slug[:-2]
        return slug

    @classmethod  # pylint: disable=too-many-arguments, too-many-positional-arguments
    def create(
        cls,
        db: Session,
        query: str,
        highlight: str,
        text: str,
        source_documents: List[str],
    ):
        """A SharedSearch model factory"""
        new_shared = cls(
            slug=cls.generate_slug(32),
            query=query,
            highlight=highlight,
            text=text,
            source_documents=",".join(source_documents or []),
        )
        db.add(new_shared)
        return new_shared
