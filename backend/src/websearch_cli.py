import argparse
import pprint

from agent.tools import search


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a web-search on SearXNG")
    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "--num-results",
        type=int,
        default=3,
        help="Number of initial search queries",
    )
    args = parser.parse_args()

    result = search.invoke(args)
    pprint.pp(result)


if __name__ == "__main__":
    main()
