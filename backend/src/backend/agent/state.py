import operator
from typing import List, TypedDict

from langgraph.graph import add_messages
from backend.agent.structs import ConductedSearchResults
from typing_extensions import Annotated


class BaseState(TypedDict):
    input_tokens_used: Annotated[int, operator.add]
    output_tokens_used: Annotated[int, operator.add]


class OverallState(BaseState):
    messages: Annotated[list, add_messages]
    search_query: Annotated[list, operator.add]
    web_research_result: Annotated[list, operator.add]
    sources_gathered: Annotated[
        list, operator.add
    ]  # ? Not sorted and verified in graph
    initial_search_query_count: int
    max_research_loops: int
    research_loops_count: int
    reasoning_model: str
    final_response: ConductedSearchResults


class Query(BaseState):
    query: str
    rationale: str


class QueryGenerationState(BaseState):
    query_list: List[Query]


class WebSearchState(BaseState):
    messages: Annotated[list, add_messages]
    search_query: str
    id: int


class ReflectionState(BaseState):
    is_sufficient: bool
    knowledge_gap: str
    follow_up_queries: Annotated[list, operator.add]
    research_loops_count: int
    number_of_ran_queries: int
