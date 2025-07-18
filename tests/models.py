from pydantic import BaseModel


class Response(BaseModel):
    ip: str
    hostname: str
    city: str
    region: str
    country: str
    loc: str
    org: str
