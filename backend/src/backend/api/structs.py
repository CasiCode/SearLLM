from pydantic import BaseModel


class InputMessage(BaseModel):
    session_id: str
    user_id: str
    message: int


class SourceDocument(BaseModel):
    source: str
    snippet: str


class OutputMessage(BaseModel):
    message: str
    source_documents: list[SourceDocument]
    session_id: str
    user_id: int
