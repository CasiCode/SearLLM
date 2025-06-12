from box import Box
import yaml


def get_config():
    with open('../config.yaml', 'r') as f:
        config_dict = yaml.safe_load(f)
    return Box(config_dict)