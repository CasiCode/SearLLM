import operator
from typing import List, TypedDict

from langgraph.graph import add_messages
from structs import ConductedSearchResults
from typing_extensions import Annotated


class OverallState(TypedDict):
    messages: Annotated[list, add_messages]
    search_query: Annotated[list, operator.add]
    web_research_result: Annotated[list, operator.add]
    sources_gathered: Annotated[list, operator.add]  # ? Used in a questionable way
    initial_search_query_count: int
    max_research_loops: int
    research_loops_count: int
    reasoning_model: str
    final_response: ConductedSearchResults


class Query(TypedDict):
    query: str
    rationale: str


class QueryGenerationState(TypedDict):
    query_list: List[Query]


class WebSearchState(TypedDict):
    messages: Annotated[list, add_messages]
    search_query: str
    id: int


class ReflectionState(TypedDict):
    is_sufficient: bool
    knowledge_gap: str
    follow_up_queries: Annotated[list, operator.add]
    research_loops_count: int
    number_of_ran_queries: int
