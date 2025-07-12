import os

import yaml
from box import Box


DIRNAME = os.path.dirname(__file__)


def get_config(path: str) -> Box:
    """
    Returns config as object.

    arguments:
        path: path to config.yml, relative to backend/src/backend/.
    returns:
        Box object holding config
    """
    abs_path = os.path.join(DIRNAME, path)
    with open(abs_path, "r") as f:
        config_dict = yaml.safe_load(f) or {}
        return Box(config_dict)
