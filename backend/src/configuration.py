import os
from typing import Any, Dict

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
from typing_extensions import Optional


class Configuration(BaseModel):
    model: str = Field(default="openai/gpt-4.1-nano")

    temperature: float = Field(default=0)

    number_of_initial_queries: int = Field(default=3)

    # Might be better to add none fields for secrets
    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        raw_values = Dict[str, Any] = {
            name: os.getenv(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }

        values = {key: value for key, value in raw_values.items() if value is not None}

        return cls(**values)
