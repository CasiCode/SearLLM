"""Contains the logic for LLM's used in the graph"""

import os

import httpx
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langchain_openai.chat_models import ChatOpenAI

from backend.agent.configuration import Configuration
from backend.utils import check_env_variables

load_dotenv()


def get_llm(config: RunnableConfig) -> ChatOpenAI:
    """
    Returns an Openrouter-provided LLM with specified configuration

    Args:
            config (RunnableConfig): LLM configuration to be used as its parameters

    Returns:
            ChatOpenAI instance
    """
    configuration = Configuration.from_runnable_config(config)

    check_env_variables(["OPENROUTER_API_KEY", "OPENROUTER_BASE_URL", "HTTP_PROXY_URL"])

    llm = ChatOpenAI(
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base=os.getenv("OPENROUTER_BASE_URL"),
        model_name=configuration.model_adress,
        temperature=configuration.temperature,
        http_client=httpx.Client(proxy=os.getenv("HTTP_PROXY_URL")),
    )
    return llm
