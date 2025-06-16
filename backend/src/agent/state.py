import operator
from typing import TypedDict

from langgraph.graph import add_messages
from typing_extensions import Annotated

from structs import ConductedSearchResults


class OverallState(TypedDict):
    messages: Annotated[list, add_messages]
    search_query: Annotated[list, operator.add]
    web_research_result: Annotated[list, operator.add]
    sources_gathered: Annotated[list, operator.add]
    initial_search_query_count: int
    max_research_loops: int
    research_loops_count: int
    reasoning_model: str
    final_response: ConductedSearchResults


class WebSearchState(TypedDict):
    messages: Annotated[list, add_messages]
    search_query: str
