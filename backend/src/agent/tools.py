from langchain_community.utilities import SearxSearchWrapper


# TODO: Setup searx engine
searx = SearxSearchWrapper(searx_host="http://127.0.0.1:8888")
