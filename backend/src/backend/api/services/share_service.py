"""Sharing manager. Saves responses from the API on demand"""

from typing import Optional


from sqlalchemy.orm import Session

from backend.api.core import structs
from backend.database.models.shared import SharedSearch
from backend.utils import get_logger


logger = get_logger(name=__name__)


class ShareService:
    """Share Service managing search sharing

    Attributes
    ----------
    db : sqlalchemy.orm.Session
        The session that will store response entries

    Methods
    -------
    share(input_message: InputMessage):
        Creates a shared response accordingly to given SharedResponse
    """

    def __init__(self, db: Session):
        self.db = db

    def share(self, response: structs.SharedSearch) -> structs.SharedSearchSlug:
        shared_search = SharedSearch.create(
            self.db,
            query=response.query,
            highlight=response.highlight,
            text=response.text,
            source_documents=response.source_documents,
        )

        self.db.commit()
        self.db.refresh(shared_search)

        logger.info("Search shared:\n%s", shared_search)

        return structs.SharedSearchSlug(slug=shared_search.slug)

    def get(self, slug: str) -> Optional[structs.SharedSearch]:
        shared_search = (
            self.db.query(SharedSearch).filter(SharedSearch.slug == slug).first()
        )

        if not shared_search:
            logger.warning(msg=f"Shared search not found with slug {slug}.")
            return None

        return structs.SharedSearch(
            query=shared_search.query,
            highlight=shared_search.highlight,
            text=shared_search.text,
            source_documents=shared_search.source_documents.split(","),
        )
