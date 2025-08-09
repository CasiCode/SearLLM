"""Agent tools"""

import json
import warnings
from typing import Dict, List, Union

from langchain_community.utilities import SearxSearchWrapper
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from backend.agent.structs import SearchArgs
from backend.utils import get_config

config = get_config("config.yml")


SEARX_HOST = f"{config.searx.host}:{str(config.searx.port)}"
searx = SearxSearchWrapper(searx_host=SEARX_HOST)


@tool(args_schema=SearchArgs)
def search(query: str) -> List[Dict]:
    """
    Use this tool to get the results of a general web search.

    Args:
        query: The target query in a text format. This exact query will be passed to web-search.

    Returns:
        A list of dictionaries with these exact keys: snippet, title, link, engines, category
    """
    return searx.results(query=query, num_results=config.searx.num_results)


def concatenate_search_results(result: Union[ToolMessage, List[ToolMessage]]) -> str:
    """
    Processes search results. Returns a concatenated string with all the valid contents included

    Args:
        result (ToolMessage | List[ToolMessage]): search results.

    Returns:
        Returns a concatenated string with all the valid contents included
    """
    if isinstance(result, ToolMessage):
        result = [result]

    text_contents = []
    for message in result:
        try:
            result_dict = json.loads(message.content)

            text_contents.append(
                "\n".join(
                    f"{str(key)}: {str(val)}"
                    for res in result_dict
                    for key, val in res.items()
                    if isinstance(res, dict)
                )
            )
        except json.JSONDecodeError as e:
            warnings.warn(
                message=f"Invalid result JSON, parsing collapsed: {e}.",
                stacklevel=2,
            )
    return "\n\n".join(text_contents)
