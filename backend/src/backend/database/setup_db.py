"""Database setup script. Intended to run once on API start"""

import logging

from backend.database.models import user, query, response, shared  # pylint: disable=unused-import
from backend.database.base import Base, engine
from backend.utils import get_logger


logger = get_logger(name=__name__)


Base.metadata.create_all(bind=engine)
logger.log(level=1, msg="Database tables created")
