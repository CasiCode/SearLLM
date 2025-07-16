"""Main app script, runs the FastAPI service via Uvicorn"""

from fastapi import FastAPI

import backend.database.setup_db  # pylint: disable=unused-import
from backend.api.core.exceptions import setup_exception_handlers
from backend.api.routers import queries


app = FastAPI()
setup_exception_handlers(app)
app.include_router(queries.router, prefix="/queries", tags=["queries"])
