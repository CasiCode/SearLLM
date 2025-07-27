"""State classes for Langgraph nodes"""

import operator
from typing import List, TypedDict

from langgraph.graph import add_messages
from typing_extensions import Annotated

from backend.agent.structs import FinalizedAnswer


class BaseState(TypedDict):
    """Base class for all other states

    Attributes
    ----------
    input_tokens_used : Annotated[int, operator.add]
        Number of input tokens used by nodes in this state
    output_tokens_used : Annotated[int, operator.add]
        Number of output tokens used by nodes in this state
    """

    input_tokens_used: Annotated[int, operator.add]
    output_tokens_used: Annotated[int, operator.add]


class OverallState(BaseState):
    """State of the main graph stream

    Attributes
    ----------
    messages : Annotated[list, add_messages]
        list of messages emmited
    search_query : Annotated[list, operator.add]
        list of search queries generated
    web_research_result : Annotated[list, operator.add]
        list of web search results found
    sources_gathered : Annotated[list, operator.add]
        list of gathered sources
    initial_search_query_count : int
        number of queries generated in the first graph node
    max_research_loops : int
        the maximum number of self-reflection loops the graph can go through
    research_loops_count : int
        current number of research loops
    reasoning_model : str
        the model to be used in the langgraph
    final_response : ConductedSearchResults
        final graph response
    """

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
    final_response: FinalizedAnswer


class Query(TypedDict):  # ? Isn't it supposed to be in structs?
    """
    A search query emmited by the graph

    Attributes
    ----------
    query : str
        query text
    rationale : str
        a brief explanation of why the query is done
    """

    query: str
    rationale: str  # ? is this even needed?


class QueryGenerationState(BaseState):
    """
    A state used in tool calling generation

    Attributes
    ----------
    query_list : List[Query]
        Queries to be done via searxng
    """

    query_list: List[Query]


class WebSearchState(BaseState):
    """
    A state of the actual web search

    Attributes
    ----------
    messages : Annotated[list, add_messages]
        list of messages emmited
    search_query : str
        a search query of this searching stream
    id : int
        id of the searching stream
    """

    messages: Annotated[list, add_messages]
    search_query: str
    id: int


class ReflectionState(BaseState):
    """
    A state of self-reflection

    Attributes
    ----------
    is_sufficient : bool
        true if the given context is sufficient to answer the question, else false
    knowledge_gap : str
        data unknown as of now but relevant to the topic
    follow_up_queries : Annotated[list, operator.add]
        queries to be done so the knowledge gap minimizes
    research_loops_count : int
        number self-reflection of loops done
    number_of_ran_queries : int
        number of ran web-search queries
    """

    is_sufficient: bool
    follow_up_queries: Annotated[list, operator.add]
    research_loops_count: int
    number_of_ran_queries: int
