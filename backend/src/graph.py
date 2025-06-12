from llm import structured_llm
from utils import get_research_topic
from state import OverallState


def generate_query(state: OverallState):
    research_topic = get_research_topic(state['messages'])