from llm import search_query_llm
from utils import (
    get_research_topic, get_config, get_current_date
)
from state import OverallState
from prompts.laoder import PromptLoader


config = get_config()


def generate_query(state: OverallState):
    research_topic = get_research_topic(state['messages'])

    if state.get('initial_search_query_count') is None:
        state['initial_search_query_count'] = config.state.number_of_initial_queries
    
    prompt = PromptLoader.get_prompt('query_writer.md')
    current_date = get_current_date()
    formatted_prompt = prompt.format(
        current_date=current_date,
        research_topic=research_topic,
        number_queries=state.get('initial_search_query_count')
    )

    result = search_query_llm.invoke(formatted_prompt)
    return {'query_list': result.query}


def web_search(state: OverallState):
    pass