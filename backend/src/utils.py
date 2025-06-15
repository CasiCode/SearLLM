from typing import List
from datetime import datetime

from box import Box
import yaml

from langchain_core.messages import (
    AnyMessage, HumanMessage, AIMessage
)


def get_current_date():
    return datetime.now().strftime('%B/%d/%Y')


def get_config():
    with open('../config.yaml', 'r') as f:
        config_dict = yaml.safe_load(f)
    return Box(config_dict)


def get_research_topic(msgs: List[AnyMessage]) -> str:
    if len(msgs) == 1:
        return msgs[-1].content.strip()
    else:
        topic = ''
        for msg in msgs:
            if isinstance(msg, HumanMessage):
                topic += f'User: {msg.content.strip()}\n'
            elif isinstance(msg, AIMessage):
                topic += f'Assistant: {msg.content.strip()}\n'
        return topic