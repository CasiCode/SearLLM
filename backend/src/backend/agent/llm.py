import os

from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langchain_openai.chat_models import ChatOpenAI

from backend.src.backend.agent.configuration import Configuration

load_dotenv()


def get_llm(config: RunnableConfig):
    configuration = Configuration.from_runnable_config(config)

    if os.getenv("OPENROUTER_API_KEY") is None:
        raise ValueError("OPENROUTER_API_KEY is not set")
    if os.getenv("OPENROUTER_BASE_URL") is None:
        raise ValueError("OPENROUTER_BASE_URL is not set")

    llm = ChatOpenAI(
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base=os.getenv("OPENROUTER_BASE_URL"),
        model_name=configuration.model,
        temperature=configuration.temperature,
    )
    return llm
