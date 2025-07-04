from fastapi import FastAPI

from backend.api.core.exceptions import setup_exception_handlers
from backend.api.routers import queries


app = FastAPI()
setup_exception_handlers(app)
app.include_router(queries.router, prefix="/queries", tags=["queries"])
