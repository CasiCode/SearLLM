from backend.src.agent.tools import searx
import pprint


print("started")
pprint.pp(searx.results(query="What's Obama's middle name?", num_results=3))
