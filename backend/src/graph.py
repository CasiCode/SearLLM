from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage

from llm import get_llm
from utils import (
    get_research_topic, get_current_date
)
from state import (
    OverallState, WebSearchState
)
from backend.src.configuration import Configuration
from backend.src.prompts.loader import PromptLoader
from backend.src.structs import SearchQueryList, ConductedSearchResults
from backend.src.tools import web_search_tool


def generate_query(state: OverallState, config: RunnableConfig):
    configuration = Configuration.from_runnable_config(config)
    research_topic = get_research_topic(state['messages'])

    if state.get('initial_search_query_count') is None:
        state['initial_search_query_count'] = configuration.number_of_initial_queries
    
    prompt = PromptLoader.load_prompt('query_writer.md')
    current_date = get_current_date()
    formatted_prompt = prompt.format(
        current_date=current_date,
        research_topic=research_topic,
        number_queries=state.get('initial_search_query_count')
    )

    llm = get_llm(config)
    search_query_llm = llm.with_structured_output(SearchQueryList)

    result = search_query_llm.invoke(formatted_prompt)
    return {'query_list': result.query}


def web_search(state: WebSearchState, config: RunnableConfig):
    prompt = PromptLoader.get_prompt('web_searcher.md')
    formatted_prompt = prompt.format(
        current_date=get_current_date,
        search_query=state['search_query']
    )

    llm = get_llm(config)
    web_search_llm = llm.bind_tools([web_search_tool])

    response = web_search_llm.invoke(formatted_prompt)
    return {'messages': [response]}


# Might be done with ONE singular node with structured output and bound tools
def process_search_results(state: WebSearchState, config: RunnableConfig):
    recent_tool_msgs = []
    for message in reversed(state['messages']):
        if message.type == 'tool' and message.artifact is not None:
            recent_tool_msgs.append(message)
        else:
            break
    tool_msgs = recent_tool_msgs[::-1]
    
    prompt_template = PromptLoader.load_prompt('search_result_proccessor.md')
    system_message_content = prompt_template.format(
        search_query=state['search_query']
    )
    prompt = [SystemMessage(system_message_content)] + tool_msgs

    llm = get_llm(config)
    processor_llm = llm.with_structured_output(ConductedSearchResults)

    response = processor_llm.invoke(prompt)