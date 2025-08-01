"""Collection of base models used for service communication and HTTP validation"""

from pydantic import BaseModel


class InputMessage(BaseModel):
    """
    Input message model

    Attributes
    ----------
    session_id : str
        unique session id used
    user_id: int
        unique user id
    message: str
        input message from the user
    """

    session_id: str
    user_id: str
    message: str


class OutputMessage(BaseModel):
    """
    Ouput message model

    Attributes
    ----------
    message : str
        full output message text
    highlight : str
        short highlight of message field
    source_documents : list[str]
        list of links used in the answer
    session_id : str
        unique session id
    input_tokens_used : int
        number of input tokens used for generation
    output_tokens_used : int
        number of output tokens used for generation
    """

    message: str
    highlight: str
    source_documents: list[str]
    session_id: str
    input_tokens_used: int
    output_tokens_used: int
