import warnings
from typing import Dict, Any

from datetime import datetime
from typing import List

import tiktoken

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from backend.agent.configuration import Configuration


def get_current_date():
    return datetime.now().strftime("%B/%d/%Y")


def get_research_topic(msgs: List[AnyMessage]) -> str:
    if len(msgs) == 1:
        return msgs[-1].content.strip()
    else:
        topic = ""
        for msg in msgs:
            if isinstance(msg, HumanMessage):
                topic += f"User: {msg.content.strip()}\n"
            elif isinstance(msg, AIMessage):
                topic += f"Assistant: {msg.content.strip()}\n"
        return topic


def get_token_usage(chat_response: Dict[str, Any]) -> Dict[str, Any]:
    usage = chat_response.additional_kwargs.get("token_usage", {})
    return {
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
    }


# TODO: Incorporate in graph and\or API to count user tokens
def num_tokens_from_messages(messages, config: RunnableConfig) -> int:
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
    elif "gpt-4" in configuration.model_name:
        print(
            "Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613."
        )
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {configuration.model_name}."""
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
