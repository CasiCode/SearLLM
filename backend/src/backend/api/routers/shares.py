"""API Routers for search sharing"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.security.runtime_auth import require_api_token
from backend.api.core.structs import (
    SharedSearchSlug,
    SharedSearch,
)
from backend.api.services.share_service import ShareService
from backend.database.base import get_db
from backend.utils import get_logger


logger = get_logger(name=__name__)

router = APIRouter(dependencies=[Depends(require_api_token)])


@router.post("/create", response_model=SharedSearchSlug)
async def share_search(
    data: SharedSearch,
    db: Session = Depends(get_db),
):
    """
    Shares API endpoint. Creates shared search entries from http requests via ShareService

    Parameters:
        data (SharedSearchInputData): SharedSearchInputData formatted from the request
    """
    service = ShareService(db=db)

    try:
        slug = service.share(data)
        return slug
    except Exception as e:
        logger.warning("Error while sharing the search: %s", e, stacklevel=3)
        return SharedSearchSlug(slug="")


@router.get("/s/{slug}", response_model=SharedSearch)
async def get_data(
    slug: str,
    db: Session = Depends(get_db),
):
    """
    Returns shared search by slug. Responses with shared search entries.

    Parameters:
        data (SharedResponseInputData): SharedResponseInputData formatted from the request
    """
    service = ShareService(db=db)

    try:
        result = service.get(slug)
        if result is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return result
    except Exception as e:
        logger.warning("Error while obtaining the search: %s", e, stacklevel=3)
        raise HTTPException(status_code=500, detail="Internal Server Error")
