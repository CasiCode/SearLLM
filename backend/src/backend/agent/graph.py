"""Contains main Langgraph logic"""

import os
import logging
from typing import Optional

import yaml

from langchain_core.messages import SystemMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.types import Send

from backend.agent.llm import get_llm
from backend.agent.state import (
    OverallState,
    QueryGenerationState,
    WebSearchState,
    ReflectionState,
)
from backend.agent.tools import search
from backend.agent.utils import get_current_date, get_research_topic
from backend.agent.configuration import Configuration
from backend.agent.prompts.loader import PromptLoader
from backend.agent.structs import (
    ConductedSearchResults,
    SearchQueryList,
    ReflectionResults,
)
from backend.agent.utils import get_token_usage


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


DIRNAME = os.path.dirname(__file__)


def generate_queries(
    state: OverallState, config: RunnableConfig
) -> QueryGenerationState:
    """
    Generates initial search queries for the target topic using LLM

    Parameters:
        state (OverallState): state of an according graph stream
        config (RunnableConfig): graph config instance

    Returns:
        QueryGenerationState
    """
    configuration = Configuration.from_runnable_config(config)
    research_topic = get_research_topic(
        state["messages"]
    )  # ! eats up a shit ton of tokens for sure

    if state.get("initial_search_query_count") is None:
        state["initial_search_query_count"] = configuration.number_of_initial_queries

    prompt = PromptLoader("query_writer.md").load_prompt()
    current_date = get_current_date()
    formatted_prompt = prompt.format(
        current_date=current_date,
        research_topic=research_topic,
        number_queries=state.get("initial_search_query_count"),
    )

    llm = get_llm(config)
    search_query_llm = llm.with_structured_output(SearchQueryList, include_raw=True)

    response = search_query_llm.invoke(formatted_prompt)
    if response["parsing_error"] is not None:
        logger.warning(
            msg="Response returned a parsing error. Falling back to raw text.",
            stacklevel=1,
        )
        query_list = SearchQueryList(
            query=[response["raw"].text],
        )  # ? Might be .content
    else:
        query_list = response["parsed"]

    token_usage = get_token_usage(response["raw"])

    logger.info("Queries generated successfully.")

    return {
        "query_list": query_list.query,
        "input_tokens_used": token_usage["prompt_tokens"],
        "output_tokens_used": token_usage["completion_tokens"],
    }


def initialize_web_search(state: QueryGenerationState):
    """
    Sends each generated query to a new context of a web_search node

    Parameters:
        state (QueryGenerationState): state of an according graph stream
    """
    return [
        Send("web_search", {"search_query": query, "id": int(idx)})
        for idx, query in enumerate(state["query_list"])
    ]


def web_search(state: WebSearchState, config: RunnableConfig) -> WebSearchState:
    """
    Generates tool-calls to search the web accoring to the given search query

    Parameters:
        state (WebSearchState): state of an according graph stream
        config (RunnableConfig): graph config instance

    Returns:
        WebSearchState
    """
    prompt = PromptLoader("web_searcher.md").load_prompt()
    formatted_prompt = prompt.format(
        current_date=get_current_date, search_query=state["search_query"]
    )

    llm = get_llm(config)
    web_search_llm = llm.bind_tools([search], tool_choice="search")

    response = web_search_llm.invoke(formatted_prompt)
    token_usage = get_token_usage(response)
    logger.info("Web search done successfully.")
    return {
        "messages": [response],
        "input_tokens_used": token_usage["prompt_tokens"],
        "output_tokens_used": token_usage["completion_tokens"],
    }


def process_search_results(
    state: WebSearchState, config: RunnableConfig
) -> OverallState:
    """
    Processes incoming tool messages and summarizes them into a cohesive text

    Parameters:
        state (WebSearchState): state of an according graph stream
        config (RunnableConfig): graph config instance

    Returns:
        OverallState
    """
    recent_tool_msgs = []
    for message in reversed(state["messages"]):
        if message.type == "tool" and message.artifact is not None:
            recent_tool_msgs.append(message)
        else:
            break
    tool_msgs = recent_tool_msgs[::-1]

    prompt_template = PromptLoader("search_result_proccessor.md").load_prompt()
    system_message_content = prompt_template.format(search_query=state["search_query"])
    prompt = [SystemMessage(system_message_content)] + tool_msgs

    llm = get_llm(config)
    processor_llm = llm.with_structured_output(ConductedSearchResults, include_raw=True)

    response = processor_llm.invoke(prompt)
    if response["parsing_error"] is not None:
        logger.warning(
            msg="Response returned a parsing error. Falling back to raw text.",
            stacklevel=1,
        )
        summary = ConductedSearchResults(
            text=response["raw"].text, sources=[]
        )  # ? Might be .content
    else:
        summary = response["parsed"]

    token_usage = get_token_usage(response["raw"])

    logger.info("Processed the results successfully.")
    return {
        "web_research_result": [summary.model_dump()] if summary else [],
        "input_tokens_used": token_usage["prompt_tokens"],
        "output_tokens_used": token_usage["completion_tokens"],
    }


def reflection(state: OverallState, config: RunnableConfig) -> ReflectionState:
    """
    This node manages graph self-reflection and tries
    to enrich the data with new queries if needed

    Parameters:
        state (OverallState): state of an according graph stream
        config (RunnableConfig): graph config instance

    Returns:
        ReflectionState
    """
    state["research_loops_count"] = state.get("research_loops_count", 0) + 1

    current_date = get_current_date()
    prompt_template = PromptLoader("reflector.md").load_prompt()

    summaries = state["web_research_result"]
    summaries_as_text = [
        summary["text"] + "\n\nSources:\n" + "\n".join(summary["sources"])
        for summary in summaries
    ]

    formatted_prompt = prompt_template.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n\n---\n\n".join(summaries_as_text),
    )

    llm = get_llm(config)
    reflector_llm = llm.with_structured_output(ReflectionResults, include_raw=True)

    response = reflector_llm.invoke(formatted_prompt)
    if response["parsing_error"] is not None:
        logger.warning(
            msg="Response returned a parsing error. Falling back to raw text.",
            stacklevel=1,
        )
        reflection = ReflectionResults(
            is_sufficient=True, follow_up_queries=[]
        )  # ? Might be better to construct a real flag and list from corrupted raw output
    else:
        reflection = response["parsed"]

    token_usage = get_token_usage(response["raw"])

    logger.info("Reflected on the response successfully.")
    return {
        "is_sufficient": reflection.is_sufficient,
        "follow_up_queries": reflection.follow_up_queries,
        "research_loops_count": state["research_loops_count"],
        "number_of_ran_queries": len(state["search_query"]),
        "input_tokens_used": token_usage["prompt_tokens"],
        "output_tokens_used": token_usage["completion_tokens"],
    }


def evaluate_research(state: ReflectionState, config: RunnableConfig):
    """
    Evaluates if the found information is sufficient enough
    to generate a final answer with

    Parameters:
        state (ReflectionState): state of an according graph stream
        config (RunnableConfig): graph config instance

    Returns:
        OverallState
    """
    configuration = Configuration.from_runnable_config(config)

    max_research_loops = configuration.max_research_loops

    if state["is_sufficient"] or state["research_loops_count"] >= max_research_loops:
        return "finalize_answer"
    return [
        Send(
            "web_search",
            {
                "search_query": query,
                "id": state["number_of_ran_queries"] + int(idx),
            },
        )
        for idx, query in enumerate(state["follow_up_queries"])
    ]


def finalize_answer(state: OverallState, config: RunnableConfig):
    """
    Generates the final graph answer

    Parameters:
        state (OverallState): state of an according graph stream
        config (RunnableConfig): graph config instance

    Returns:
        json-like dictionary
    """
    current_date = get_current_date()
    prompt_template = PromptLoader("answerer.md").load_prompt()

    summaries = state["web_research_result"]
    summaries_as_text = [
        summary["text"] + "\n\nSources:\n" + "\n".join(summary["sources"])
        for summary in summaries
    ]

    formatted_prompt = prompt_template.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n\n---\n\n".join(summaries_as_text),
    )

    llm = get_llm(config)
    response = llm.invoke(formatted_prompt)
    token_usage = get_token_usage(response)

    unique_sources = {source for summary in summaries for source in summary["sources"]}

    logger.info("Answer finalized successfully.")

    return {
        "messages": [AIMessage(content=response.content)],
        "sources_gathered": list(unique_sources),
        "input_tokens_used": token_usage["prompt_tokens"],
        "output_tokens_used": token_usage["completion_tokens"],
    }


workflow = StateGraph(state_schema=OverallState, config_schema=Configuration)

workflow.add_node("generate_query", generate_queries)
workflow.add_node("web_search", web_search)
workflow.add_node("web_search_tools", ToolNode([search]))
workflow.add_node("process_search_results", process_search_results)
workflow.add_node("reflection", reflection)
workflow.add_node("evaluation", evaluate_research)
workflow.add_node("finalize_answer", finalize_answer)

workflow.set_entry_point("generate_query")

workflow.add_conditional_edges("generate_query", initialize_web_search, ["web_search"])
workflow.add_edge("web_search", "web_search_tools")
workflow.add_edge("web_search_tools", "process_search_results")
workflow.add_edge("process_search_results", "reflection")
workflow.add_conditional_edges(
    "reflection", evaluate_research, ["web_search", "finalize_answer"]
)
workflow.add_edge("finalize_answer", END)


def process_input_message(input_message: str, config: Optional[dict[str, any]] = None):
    """
    Processes a message catched through the API.

    Args:
      session_id - id of current session.
      input_message - query message.

    Returns:
      model answer, sources, session_id, user_id. Aligns with pydantic-model for output messages.
    """

    graph = workflow.compile()

    abs_path = os.path.join(DIRNAME, "config.yml")
    config_dict = {}
    if config:
        config_dict = config()
    else:
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                config_dict = yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning("Config file not found, loading empty config.", stacklevel=1)

    config = RunnableConfig(configurable=config_dict.get("configurable", {}))

    response = graph.invoke(
        {"messages": [{"role": "user", "content": input_message}]},
        stream_mode="values",
        config=config,
    )

    src = []
    if response.get("sources_gathered") and len(response["sources_gathered"]) > 0:
        for source in response["sources_gathered"]:
            if isinstance(source, dict):
                src.append({"source": source["link"], "snippet": source["snippet"]})
            else:
                src.append(
                    {
                        "source": "unknown",
                        "snippet": f"Unexpected search data recieved: {type(source)}",
                    }
                )

    return {
        "message": response["messages"][-1].content
        if response.get("messages")
        else "Oops, we couldn't proccess your message, sorry!",
        "source_documents": src,
        "input_tokens_used": response["input_tokens_used"],
        "output_tokens_used": response["output_tokens_used"],
    }
