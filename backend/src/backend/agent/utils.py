"""Graph utils"""

import warnings
from datetime import datetime
from typing import Any, Dict, List

import tiktoken
from langchain_core.messages import BaseMessage, AIMessage, AnyMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from backend.agent.configuration import Configuration


def get_current_date():
    """
    Get current date as string
    """
    return datetime.now().strftime("%B/%d/%Y")


def get_research_topic(msgs: List[AnyMessage]) -> str:
    """
    Get research topic context

    Args:
      msgs (List[AnyMessage]): list of messages in context

    Returns:
      string with concatenated messages marked
      with user/assistant tag accordingly
    """
    if len(msgs) == 1:
        return msgs[-1].content.strip()
    topic = ""
    for msg in msgs:
        if isinstance(msg, HumanMessage):
            topic += f"User: {msg.content.strip()}\n"
        elif isinstance(msg, AIMessage):
            topic += f"Assistant: {msg.content.strip()}\n"
    return topic


def get_token_usage(chat_response: BaseMessage) -> Dict[str, Any]:
    """
    Get the precise token usage for an LLM call

    Args:
      chat_response (BaseMessage): LLM API response

    Returns:
      dict with these exact keys:
      prompt_tokens, completion_tokens, total_tokens
    """
    usage = chat_response.usage_metadata
    return {
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
    }


def num_tokens_from_messages(messages, config: RunnableConfig) -> int:
    """
    Get the estimated token usage for given messages

    Args:
      messages (List[BaseMessage]): messages to be estimated
      config (RunnableConfig): graph config used while generating messages

    Returns:
      Estimated token usage as integer number
    """
    configuration = Configuration.from_runnable_config(config)

    try:
        encoding = tiktoken.encoding_for_model(configuration.model_name)
    except KeyError:
        warnings.warn(
            message="Model not found. Using o200k_base encoding.",
            stacklevel=3,
            category=RuntimeWarning,
        )
        encoding = tiktoken.get_encoding("o200k_base")

    if configuration.model_name in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif configuration.model_name == "gpt-3.5-turbo-0301":
        tokens_per_message = 4
        tokens_per_name = -1
    elif configuration.model_name == "gpt-4.1-nano":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(
            f"""
            num_tokens_from_messages() is not implemented for model {configuration.model_name}.
            """
        )

    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name

    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens
