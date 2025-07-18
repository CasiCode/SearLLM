import argparse

from langchain_core.messages import HumanMessage

from backend.agent.graph import process_input_message


def main() -> None:
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
        help="LLM used to conduct the research",
    )

    args = parser.parse_args()

    config = {
        "messages": [HumanMessage(content=args.question)],
        "number_of_initial_queries": args.initial_queries,
        "max_research_loops": args.max_loops,
        "model_address": args.model_address,
    }

    result = process_input_message(input_message=args.question, config=config)
    print(result.get("message", ""))


if __name__ == "__main__":
    main()
