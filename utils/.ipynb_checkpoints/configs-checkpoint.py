import os
import yaml

def get_config():
    """Get config from yaml file ex: get_config('desktop_config.yml')"""
    with open(os.path.dirname(os.path.abspath("desktop_config.yml"))+"/utils/desktop_config.yml") as file:
        fruits_list = yaml.load(file, Loader=yaml.FullLoader)
    return fruits_list