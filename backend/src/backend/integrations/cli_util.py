"""A CLI util integration"""

import argparse
import locale

from langcodes import Language

from langchain_core.messages import HumanMessage

from backend.agent.graph import process_input_message


def main() -> None:
    """
    Processes a command line query

    Parameters (inline):
        question (str): Research question
        initial-queries (int): Number of initial search queries
        max-loops (int): Maximum number of research loops
        model_address (str): Full provider address of the LLM used to conduct the research

    Returns:
        json-like dictionary
    """
    parser = argparse.ArgumentParser(description="Run the research agent")
    parser.add_argument("question", help="Research question")
    parser.add_argument(
        "--initial-queries",
        type=int,
        default=3,
        help="Number of initial search queries",
    )
    parser.add_argument(
        "--max-loops", type=int, default=3, help="Maximum number of research loops"
    )
    parser.add_argument(
        "--model_address",
        type=str,
        default="openai/gpt-4.1-nano",
        help="Full provider address of the LLM used to conduct the research",
    )

    args = parser.parse_args()

    config = {
        "messages": [HumanMessage(content=args.question)],
        "number_of_initial_queries": args.initial_queries,
        "max_research_loops": args.max_loops,
        "model_address": args.model_address,
    }

    language_code = locale.getdefaultlocale()[0]
    language = Language.make(language=language_code).display_name

    result = process_input_message(
        input_message=args.question, language=language, config=config
    )
    print(result.get("message", ""))


if __name__ == "__main__":
    main()
