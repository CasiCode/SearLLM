"""Main pydandic models used in graph logic"""

from typing import List

from pydantic import BaseModel, Field


class SearchQueryList(BaseModel):
    """A list of search queries to be used for web research

    Attributes
    ----------
    query : List[str]
    """

    query: List[str] = Field(
        description="A list of search queries to be used for web research"
    )


class ConductedSearchResults(BaseModel):
    """Search results conducted into a cohesive summary

    Attributes
    ----------
    text : str
        Verifiable text artifact. Well-written summary based on the search findings
    sources : List[str]
        A list of gathered sources
    """

    # pylint: disable=line-too-long
    text: str = Field(
        description="Verifiable text artifact. Well-written summary or report based on the search findings"
    )
    sources: List[str] = Field(description="A list of gathered sources")


class ReflectionResults(BaseModel):
    """Self-reflection results

    Attributes
    ----------
    is_sufficient : bool
        Boolean flag showing if the input summary is sufficient
    follow_up_queries : List[str]
        List of generated follow-up queries to adress the knowledge gap
    """

    is_sufficient: bool = Field(
        description="Boolean flag showing if the input summary is sufficient"
    )
    follow_up_queries: List[str] = Field(
        description="List of generated follow-up queries to adress the knowledge gap"
    )


class SearchArgs(BaseModel):
    """Arguments schema for the search tool

    Attributes
    ----------
    query : str
        The target query in a text format. This exact query will be passed to web-search
    num_results : int
        The number of results to be returned by the tool
    """

    # pylint: disable=line-too-long
    query: str = Field(
        description="The target query in a text format. This exact query will be passed to web-search."
    )
    num_results: int = Field(
        description="The number of results to be returned by the tool. Each result contains these exact fields: snippet, title, link, engines, category",
        default=5,
    )
