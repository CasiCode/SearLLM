import logging

from backend.database.models import user, query, response  # pylint: disable=unused-import
from backend.database.base import Base, engine


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


Base.metadata.create_all(bind=engine)
logger.log(level=1, msg="Database tables created")
