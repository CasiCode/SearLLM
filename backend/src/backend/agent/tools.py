import warnings
from typing import Dict, List

from langchain_community.utilities import SearxSearchWrapper
from langchain_core.tools import tool

from backend.agent.structs import SearchArgs

# TODO: Make an LLM able to utilize tool arguments smarter
# TODO: Rewrite searcher prompt to constrain min and max num_results


# TODO: Check if this line changes with new app architecture
searx = SearxSearchWrapper(searx_host="http://127.0.0.1:8888")  # ! MUST BE IN CONFIG


@tool(args_schema=SearchArgs)
def search(query: str, num_results: int) -> List[Dict]:
    """
    Use this tool to get the results of a general web search.

    Args:
        query: The target query in a text format. This exact query will be passed to web-search.
        num_results: The number of results to be returned by the tool.

    Returns:
        A list of dictionaries with these exact keys: snippet, title, link, engines, category
    """
    if num_results < 1:
        warnings.warn(
            message=f"num_results set to {num_results}",
            stacklevel=3,
            category=RuntimeWarning,
        )
        num_results = 1

    if num_results > 10:
        warnings.warn(
            message=f"num_results set to {num_results}",
            stacklevel=3,
            category=RuntimeWarning,
        )
        num_results = 10

    return searx.results(query=query, num_results=num_results)
