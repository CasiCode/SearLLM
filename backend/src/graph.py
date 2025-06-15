from langchain_core.runnables import RunnableConfig

from llm import get_llm
from utils import (
    get_research_topic, get_current_date
)
from state import OverallState
from configuration import Configuration
from prompts.laoder import PromptLoader
from tools import SearchQueryList


def generate_query(state: OverallState, config: RunnableConfig):
    configuration = Configuration.from_runnable_config(config)
    research_topic = get_research_topic(state['messages'])

    if state.get('initial_search_query_count') is None:
        state['initial_search_query_count'] = configuration.number_of_initial_queries
    
    prompt = PromptLoader.get_prompt('query_writer.md')
    current_date = get_current_date()
    formatted_prompt = prompt.format(
        current_date=current_date,
        research_topic=research_topic,
        number_queries=state.get('initial_search_query_count')
    )

    search_query_llm = get_llm(config, SearchQueryList)

    result = search_query_llm.invoke(formatted_prompt)
    return {'query_list': result.query}


def web_search(state: OverallState):
    pass