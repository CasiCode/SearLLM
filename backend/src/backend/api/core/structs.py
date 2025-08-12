"""Collection of base models used for service communication and HTTP validation"""

from typing import Optional

from pydantic import BaseModel


class InputMessage(BaseModel):
    """
    Input message model

    Attributes
    ----------
    session_id : str
        unique session id used
    user_id: str
        unique user id
    message: str
        input message from the user
    language: str
        preffered language
    """

    session_id: str
    user_id: str
    message: str
    pref_language: Optional[str] = "en"


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


class SharedSearch(BaseModel):
    """
    Shared search data model

    Attributes
    ----------
    query : str
        original query
    highlight : str
        short highlight of message field
    text : str
        full output message text
    source_documents : list[str]
        list of links used in the answer
    """

    query: str
    highlight: str
    text: str
    source_documents: list[str]


class SharedSearchSlug(BaseModel):
    """
    Shared search data model

    Attributes
    ----------
    slug : str
        unique string identifier of the shared response
    """

    slug: str
