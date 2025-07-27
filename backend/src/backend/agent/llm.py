"""Contains the logic for LLM's used in the graph"""

import os
import logging

import httpx
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langchain_openai.chat_models import ChatOpenAI

from backend.agent.configuration import Configuration
from backend.utils import check_env_variables

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_llm(config: RunnableConfig) -> ChatOpenAI:
    """
    Returns an Openrouter-provided LLM with specified configuration

    Args:
            config (RunnableConfig): LLM configuration to be used as its parameters

    Returns:
            ChatOpenAI instance
    """
    configuration = Configuration.from_runnable_config(config)

    check_env_variables(
        [
            "OPENROUTER_API_KEY",
            "OPENROUTER_BASE_URL",
        ]
    )

    try:
        check_env_variables("SAFE_PROXY_URL")
        proxy_client = httpx.Client(proxy=os.getenv("SAFE_PROXY_URL"))
    except ValueError:
        logger.warning(msg="SAFE_PROXY_URL not provided, falling back to direct HTTP")
        proxy_client = None

    llm = ChatOpenAI(
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base=os.getenv("OPENROUTER_BASE_URL"),
        model_name=configuration.model_adress,
        temperature=configuration.temperature,
        http_client=proxy_client,
    )
    return llm
