from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import Send

from backend.src.agent.llm import get_llm
from backend.src.agent.state import (
    OverallState,
    QueryGenerationState,
    WebSearchState,
    ReflectionState,
)
from backend.src.agent.tools import web_search_tool
from backend.src.agent.utils import get_current_date, get_research_topic
from backend.src.configuration import Configuration
from backend.src.prompts.loader import PromptLoader
from backend.src.structs import (
    ConductedSearchResults,
    SearchQueryList,
    ReflectionResults,
)


def generate_query(state: OverallState, config: RunnableConfig):
    configuration = Configuration.from_runnable_config(config)
    research_topic = get_research_topic(state["messages"])

    if state.get("initial_search_query_count") is None:
        state["initial_search_query_count"] = configuration.number_of_initial_queries

    prompt = PromptLoader.load_prompt("query_writer.md")
    current_date = get_current_date()
    formatted_prompt = prompt.format(
        current_date=current_date,
        research_topic=research_topic,
        number_queries=state.get("initial_search_query_count"),
    )

    llm = get_llm(config)
    search_query_llm = llm.with_structured_output(SearchQueryList)

    result = search_query_llm.invoke(formatted_prompt)
    return {"query_list": result.query}


def continue_web_search(state: QueryGenerationState):
    return [
        Send("web_search", {"search_query": query, "id": int(idx)})
        for idx, query in enumerate(state["query_list"])
    ]


# TODO: review and work on websearch node structure
# * We pretty much don't need this three nodes, only two: websearcher and output formatter
# ? How will the proccessor behave on multiple searches tho?
# * Seems like the desired pipeline is web_search => summary ---> process_search_results => structured_output
def web_search(state: WebSearchState, config: RunnableConfig):
    prompt = PromptLoader.get_prompt("web_searcher.md")
    formatted_prompt = prompt.format(
        current_date=get_current_date, search_query=state["search_query"]
    )

    llm = get_llm(config)
    web_search_llm = llm.bind_tools([web_search_tool])

    response = web_search_llm.invoke(formatted_prompt)
    return {"messages": [response]}


# ? Do we need it? And what is 'continue' actually? Why don't we just route to web_search again?
def should_continue(state: OverallState):
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return "process"
    else:
        return "continue"


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

    return {"final_response": response}


def reflection(state: OverallState, config: RunnableConfig) -> ReflectionState:
    state["research_loops_count"] = state.get("research_loops_count", 0) + 1

    current_date = get_current_date()
    prompt_template = PromptLoader.load_prompt("reflector.md")
    formatted_prompt = prompt_template.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n\n---\n\n".join(state["web_research_result"]),
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


# TODO: Write the thing
def finalize_answer(state: OverallState, config: RunnableConfig):
    pass


workflow = StateGraph(OverallState)

workflow.add_node("generate_query", generate_query)
workflow.add_node("web_search", web_search)
workflow.add_node("web_search_tools", ToolNode([web_search_tool]))
workflow.add_node("process_search_results", process_search_results)

workflow.set_entry_point("generate_query")

workflow.add_conditional_edges(
    "generate_query",
    should_continue,
    {"continue": "web_search", "process": "process_seach_results"},
)

workflow.add_edge("web_seach_tools", "generate_query")
workflow.add_edge("process_search_results", END)

graph = workflow.compile()


# ? the response structure will most surely change later when implementing frontend
def process_input_message(session_id: str, input_message: str, config: RunnableConfig):
    """
    Processes a message catched through the API.

    Args:
      session_id.
      input_message.

    Returns:
      model answer, sources, session_id. Aligns with pydantic-model for output messages.
    """

    response = graph.invoke(
        {"messages": [{"role": "user", "content": input_message}]},
        stream_mode="values",
        config=config,
    )

    src = []
    if response.get("context") and len(response["context"]) > 0:
        for doc in response["context"]:
            if isinstance(doc, dict):
                src.append({"source": doc["link"], "snippet": doc["snippet"]})
            else:
                src.append(
                    {
                        "source": "unknown",
                        "snippet": f"Unexpected search data recieved: {type(doc)}",
                    }
                )

    return {
        "message": response["messages"][-1].content
        if response.get("messages")
        else "Oops, we couldn't proccess your message, sorry!",
        "source_documents": src,
        "session_id": session_id,
    }
