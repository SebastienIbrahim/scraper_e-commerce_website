import os
import yaml

def get_config(device: str = "desktop"):

    """Get config from yaml file ex: get_config('desktop_config.yml')"""
    with open(os.path.dirname(os.path.abspath(f"{device}_config.yml"))+"/utils/desktop_config.yml", "r") as file:
        return yaml.safe_load(file) or {}
