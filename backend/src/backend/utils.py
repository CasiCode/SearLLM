import os
import warnings

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
    try:
        with open(abs_path, "r") as f:
            config_dict = yaml.safe_load(f) or {}
        return Box(config_dict)
    except Exception as e:
        warnings.warn(message=f"Oops, error occured! {e}", stacklevel=3)

        # ! Should raise an error instead
