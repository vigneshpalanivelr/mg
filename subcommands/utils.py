#!/usr/bin/python

"""
Utility function for the mg command
"""

import yaml
import logging


logger = logging.getLogger('__name__')

def get_config(config_file):
    """
     Parses the config file and returns it as a dict 
    """
    try:
        with open(config_file) as yaml_file:
            config = yaml.safe_load(yaml_file)
    except yaml.YAMLError as exc:
        logger.error(f"Unable to load config file {config_file}. Details:", str(exc))
        return None
    return config


def get_product_data(config, schema_file, schema_path, schema_branch, sync=False):
    """
    Find the product data, optionally sync it, read it in, and then return it
    """
    if schema_file:
        return [source_schema_file(schema_file)]
