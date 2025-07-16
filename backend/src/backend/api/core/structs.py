from pydantic import BaseModel


class InputMessage(BaseModel):
    session_id: str
    user_id: int
    message: str


class SourceDocument(BaseModel):  # ! Unused now, refactor the code to use list of str
    source: str
    snippet: str


class OutputMessage(BaseModel):
    message: str
    source_documents: list[str]
    session_id: str
    input_tokens_used: int
    output_tokens_used: int
