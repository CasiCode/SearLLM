from datetime import datetime
from typing import List

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage


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
