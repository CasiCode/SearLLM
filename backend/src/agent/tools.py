import warnings

from langchain_community.utilities import SearxSearchWrapper
from langchain_core.tools import tool
from structs import SearchArgs

# TODO: Make an LLM able to utilize tool arguments smarter


searx = SearxSearchWrapper(searx_host="http://127.0.0.1:8888")


@tool(args_schema=SearchArgs)
def search(query: str, num_results: int):
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
