from typing import List

from pydantic import BaseModel, Field


class SearchQueryList(BaseModel):
    query: List[str] = Field(
        description='A list of search queries to be used for web research'
    )
    rationale: str = Field(
        description='A brief explanation of why this queries are relevant to the research topic.'
    )


class ConductedSearchResults(BaseModel):
    text: str = Field(
        description='Verifiable text artifact. Well-written summary or report based on the search findings'
    )