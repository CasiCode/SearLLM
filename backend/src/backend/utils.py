"""A collection of utils used in numerous submodules"""

import os
from typing import Union

import yaml
from box import Box


DIRNAME = os.path.dirname(__file__)


def get_config(path: str) -> Box:
    """
    Returns config as object.

    Parameters:
        path: path to config.yml, relative to backend/src/backend/.
    Returns:
        Box object holding config
    """
    abs_path = os.path.join(DIRNAME, path)
    with open(abs_path, "r", encoding="utf-8") as f:
        config_dict = yaml.safe_load(f) or {}
        return Box(config_dict)


def check_env_variables(names: Union[str, list[str]]):
    """
    Checks if given names are present in env.

    Parameters:
        names (list[str]): list of env variable names to check for presence
    Raises:
        ValueError for the first name in names which is not present in env
    """
    if isinstance(names, str):
        names = [names]
    for name in names:
        if os.getenv(name) is None:
            raise ValueError(f"{name} is not set")
