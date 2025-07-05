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


def generate_queries(state: OverallState, config: RunnableConfig):
    configuration = Configuration.from_runnable_config(config)
    research_topic = get_research_topic(state["messages"])

    if state.get("initial_search_query_count") is None:
        state["initial_search_query_count"] = configuration.number_of_initial_queries

    prompt = PromptLoader.load_prompt("query_writer.md")
    current_date = get_current_date()
    formatted_prompt = prompt.format(
        current_date=current_date,
        research_topic=research_topic,
        number_queries=state.get("initial_search_query_count"),  # ! Might be a bug
    )

    llm = get_llm(config)
    search_query_llm = llm.with_structured_output(SearchQueryList)

    result = search_query_llm.invoke(formatted_prompt)
    return {"query_list": result.query}


def initialize_web_search(state: QueryGenerationState):
    return [
        Send("web_search", {"search_query": query, "id": int(idx)})
        for idx, query in enumerate(state["query_list"])
    ]


def web_search(state: WebSearchState, config: RunnableConfig):
    prompt = PromptLoader.load_prompt("web_searcher.md")
    formatted_prompt = prompt.format(
        current_date=get_current_date, search_query=state["search_query"]
    )

    llm = get_llm(config)
    web_search_llm = llm.bind_tools([search])

    response = web_search_llm.invoke(formatted_prompt)
    return {"messages": [response]}


# TODO: Make model gather sources from tool messages and put them in response
def process_search_results(
    state: WebSearchState, config: RunnableConfig
) -> OverallState:
    recent_tool_msgs = []
    for message in reversed(state["messages"]):
        if message.type == "tool" and message.artifact is not None:
            recent_tool_msgs.append(message)
        else:
            break
    tool_msgs = recent_tool_msgs[::-1]

    prompt_template = PromptLoader.load_prompt("search_result_proccessor.md")
    system_message_content = prompt_template.format(search_query=state["search_query"])
    prompt = [SystemMessage(system_message_content)] + tool_msgs

    llm = get_llm(config)
    processor_llm = llm.with_structured_output(ConductedSearchResults)
    response = processor_llm.invoke(prompt)

    return {"web_research_result": [response]}


def reflection(state: OverallState, config: RunnableConfig) -> ReflectionState:
    state["research_loops_count"] = state.get("research_loops_count", 0) + 1

    current_date = get_current_date()
    prompt_template = PromptLoader.load_prompt("reflector.md")

    summaries = state["web_research_result"]
    summaries_as_text = [
        "\n\nSources:\n".join(summary["text"], "\n".join(summary["sources"]))
        for summary in summaries
    ]

    formatted_prompt = prompt_template.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n\n---\n\n".join(summaries_as_text),
    )

    llm = get_llm(config)
    reflector_llm = llm.with_structured_output(ReflectionResults)
    response = reflector_llm.invoke(formatted_prompt)

    return {
        "is_sufficient": response.is_sufficient,
        "knowledge_gap": response.knowledge_gap,
        "follow_up_queries": response.follow_up_queries,
        "research_loops_count": state["research_loops_count"],
        "number_of_ran_queries": len(state["search_query"]),
    }


def evaluate_research(state: ReflectionState, config: RunnableConfig) -> OverallState:
    configuration = Configuration.from_runnable_config(config)

    max_research_loops = configuration.max_research_loops

    if state["is_sufficient"] or state["research_loops_count"] >= max_research_loops:
        return "finalize_answer"
    else:
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
    current_date = get_current_date()
    prompt_template = PromptLoader.load_prompt("answerer.md")

    summaries = state["web_research_result"]
    summaries_as_text = [
        "\n\nSources:\n".join(summary["text"], "\n".join(summary["sources"]))
        for summary in summaries
    ]

    formatted_prompt = prompt_template.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n\n---\n\n".join(summaries_as_text),
    )

    llm = get_llm(config)
    response = llm.invoke(formatted_prompt)

    unique_sources = {source for summary in summaries for source in summary["sources"]}

    return {
        "messages": [AIMessage(content=response.content)],
        "sources_gathered": unique_sources,
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

graph = workflow.compile()


# ! How to even register it in API if it has config in args?
# ? the response structure will most surely change later when implementing frontend
def process_input_message(
    session_id: str, user_id: int, input_message: str, config: RunnableConfig
):
    """
    Processes a message catched through the API.

    Args:
      session_id - id of current session.
      user_ud - id of user which issued a query
      input_message - query message.

    Returns:
      model answer, sources, session_id, user_id. Aligns with pydantic-model for output messages.
    """

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
        "session_id": session_id,
        "user_id": user_id,
    }
