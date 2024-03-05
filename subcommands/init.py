#!/usr/bin/python

"""
Module for handling the mgit init command, which can be used to initialize new repos
"""
import subcommands
import os
import logging

logger = logging.getLogger(__name__)


def run(args, repo_data):
    """ Main function for the init command """
    cmd = "git init -q"
    paths = subcommands.Repo.get_repo_clone_paths(repo_data)
    for path in paths:
        os.makedirs(path, exist_ok=True)
    logger.debug(f"Repos paths are created: {paths}")
    return subcommands.executor.run_in_repos(paths, cmd)