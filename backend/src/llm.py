import os
from dotenv import load_dotenv

from langchain_openai.chat_models import ChatOpenAI

from backend.src.utils import get_config
from backend.src.tools import SearchQueryList


config = get_config()

load_dotenv()

if os.environ.get('OPENROUTER_API_KEY') is None:
    raise ValueError('OPENROUTER_API_KEY is not set')
if os.environ.get('OPENROUTER_BASE_URL') is None:
    raise ValueError('OPENROUTER_BASE_URL is not set')

llm = ChatOpenAI(
    openai_api_key=os.environ.get('OPENROUTER_API_KEY'),
    openai_api_base=os.environ.get('OPENROUTER_BASE_URL'),
    model_name=config.model.name,
    temperature=config.model.temperature
)

structured_llm = llm.with_structured_output(SearchQueryList)