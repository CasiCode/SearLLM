import os

from langchain_openai.chat_models import ChatOpenAI

from backend.src.utils import get_config
from backend.src.tools import SearchQueryList


config = get_config()

llm = ChatOpenAI(
    openai_api_key=os.environ.get('OPENROUTER_API_KEY'),
    openai_api_base=os.environ.get('OPENROUTER_BASE_URL'),
    model_name=config.model.name,
    temperature=config.model.temperature
)

structured_llm = llm.with_structured_output(SearchQueryList)