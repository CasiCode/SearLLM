"""Configuration class used as a graph config."""

import os
from typing import Any, Dict, Optional

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field


class Configuration(BaseModel):
    """Configuration

    Attributes
    ----------
    model_adress : str
        Full LLM adress as given by the model provider
    model_name : str
        General model name
    temperature : float
        Model temperature
    number_of_initial_queries : int
        Number of queries generated in the first graph node
    max_research_loops : int
        The maximum number of self-reflection loops the graph can go through

    Methods
    -------
    from_runnable_config(config: Optional[RunnableConfig]):
        Imports RunnableConfig instance into the instance of Configuration,
        sets environmental variables as default

    """

    model_adress: str = Field(default="openai/gpt-4.1-nano")
    model_name: str = Field(default="gpt-4.1-nano")

    temperature: float = Field(default=0)

    number_of_initial_queries: int = Field(default=3)

    max_research_loops: int = Field(default=3)

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        # TODO: Add env variables for dict keys
        raw_values: Dict[str, Any] = {
            name: os.getenv(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }

        values = {key: value for key, value in raw_values.items() if value is not None}

        return cls(**values)
