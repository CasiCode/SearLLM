# SearXTG

SearXTG is a backend application that conducts in-depth research on user queries by dynamically generating search terms, utilizing a private SearXNG instance to search the web, analyzing the results to identify knowledge gaps, and iteratively refining its searches until it can deliver a thoroughly supported answer with citations.

## Architecture overview

This application follows a hybrid multiservice architecture:

- **Modular Monolith**:
    The core of the application is a modular monolith, where related features are organized into distinct, well-encapsulated modules within a single codebase and deployment unit. This allows for clear separation of concerns and easier maintainability, while benefiting from the performance and simplicity of a monolithic deployment. All the modules are ready for standalone deployment as they are communicating via a middleware RESTful API powered by FastAPI framework.
    The list of monolith modules includes:
    - **api** - a monolith core. Acts as a middleware FastAPI service which orchestrates all the other modules.
    - **agent** - a Langgraph powered agentic backend for question-answering.
    - **database** - an SQLAlchemy powered database storing anonymized requests and responses and plain user data for token limit tracking.
    - **integrations** - the application currently supports and focuses on the telegram bot integration to provide messager users with this tool.
    - **security** - a collection of security utilities used in the application.


- **Independent Services**:
    In addition to the modular monolith, the system includes four independent services. These services are configured, deployed, and scaled separately from the monolith. They communicate with the monolith and, if necessary, with each other via HTTP/HTTPS RESTful APIs.
    The list of independent services includes:
    - **A private SearXNG instance** - a powerful open-source metasearch engine which aggregates results from various search services and databases.
    - **Caddy** - used as a rate-limiting backward proxy for the searxng.
    - **Redis\Valkey** - SearXNG dependency used for rate limiting and security measures.


## How the Backend Agent Works (High-Level)

The core of the backend is a LangGraph agent defined in `backend/src/agent/graph.py`. It follows these steps:

<img src="./agent-diagram.png" title="Agent Flow" alt="Agent Flow" width="75%">

1.  **Generate Initial Queries:** Based on your input, it generates a set of initial search queries using an OpenAI GPT model.
2.  **Web Research:** For each query, it uses the Gemini model with a local instanse of SearXNG host to find relevant web pages.
3.  **Reflection & Knowledge Gap Analysis:** The agent analyzes the search results to determine if the information is sufficient or if there are knowledge gaps. It uses the same model for this reflection process.
4.  **Iterative Refinement:** If gaps are found or the information is insufficient, it generates follow-up queries and repeats the web research and reflection steps (up to a configured maximum number of loops).
5.  **Finalize Answer:** Once the research is deemed sufficient, the agent synthesizes the gathered information into a coherent answer, including citations from the web sources, using the same OpenAI GPT model.
