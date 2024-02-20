#!/usr/bin/python

"""
Utility function for the mg command
"""

import yaml
import logging
import os

from subcommands import executor


logger = logging.getLogger(__name__)

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


def find_mgit(target_directory):
    """
    Search for .multigit directory
    """
    current_dir = os.getcwd()
    while current_dir != os.sep and current_dir != os.path.abspath(os.sep):
        if target_directory in os.listdir(current_dir):
            os.chdir(current_dir)
            logger.debug(f"Found MultiGit directory: {current_dir}")
            break
        current_dir = os.path.dirname(current_dir)
        logger.debug(f"Couldn't Find MultiGit directory in: {current_dir}")


def update_product_repos(config, clone_dir):
    """
    Clone all the repos to the specified dir from the product yaml file
    """
    git_server = "{}{}".format(config['server'], config['products_path'])
    if os.path.isdir(clone_dir):
        message = f"Updating products repo {git_server}..."
        executor.run(["git", "fetch", "origin"], message, cwd=clone_dir)
    else:
        message = f"Cloning products repo {git_server}..."
        executor.run(["git", "clone", git_server, os.path.basename(clone_dir)], message, cwd=os.path.dirname(clone_dir))


def get_product_contents(product_file):
    """
    Read in the provided schema file and return the data
    """
    with open(product_file) as file_contents:
        return yaml.safe_load(file_contents)


def get_product_data(product_file, product_path, multigit_dir, config, sync=False):
    """
    Find the product data, optionally sync it, read it in, and then return it
    """
    if product_file:
        logger.debug(f"Loading products details : {product_file}")
        return [get_product_contents(product_file)]
    
    # If .multigit directory is not present, it will setup in CWD
    if not product_path:
        product_path = os.path.join(os.getcwd(), multigit_dir, "products")
        logger.debug(f"Setting-up products path under: {product_path}")
    
    if sync:
        logger.debug(f"Check/Create Product directory: {os.path.dirname(product_path)}")
        os.makedirs(os.path.dirname(product_path), exist_ok=True)
        update_product_repos(config, product_path)

