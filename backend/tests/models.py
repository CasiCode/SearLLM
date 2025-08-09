"""A collection of models used in testing scripts"""

from pydantic import BaseModel


class IPInfoResponse(BaseModel):
    """Base model for IP info API response

    Attributes
    ----------
    query : List[str]
    """

    ip: str
    city: str
    region: str
    country: str
    loc: str
    org: str
