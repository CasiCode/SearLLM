from sqlalchemy import create_engine

from backend.utils import get_config


config = get_config("database/config.yml")


engine = create_engine(config.database.url)
