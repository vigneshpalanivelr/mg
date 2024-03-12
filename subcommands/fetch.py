#!/usr/bin/python

"""
Module for handling the mgit fetch command, which can be used to fetch upstream references for multiple repos
"""

import subcommands
from subcommands import executor


def parse_args(parser):
    """ Argument parsing for the fetch command """
    submodule_parser = parser.add_mutually_exclusive_group()
    submodule_parser.add_argument('--depth',
                                  help="Fetch a history truncated to the specified number of revisions")
    submodule_parser.add_argument('--recurse-submodules', dest='recursive', action='store_true',
                                  help="Recursively fetch all submodules within, using their default settings")
    parser.add_argument('--unshallow', action='store_true',
                        help="Fetch the full history of a shallow-cloned repo")
    parser.add_argument('--prune', action='store_true',
                        help="Prune remote-tracking references that no longer exist in the remote")
    parser.add_argument('--heads', action='store_true',
                        help="Fetch all remote branches from the remote named origin")
    parser.add_argument('--tags', action='store_true',
                        help="Fetch all remote tags")
    parser.set_defaults(func=run)


def run(args, repo_data):
    """ Main function for the fetch command """
    cmd = "git fetch"
    if args.depth:
        cmd += f" --depth {args.depth} --no-recurse-submodules"
    elif args.recursive:
        cmd += " --recurse-submodules"
    if args.unshallow:
        cmd += f" --unshallow"
    if args.prune:
        cmd += " --prune"
    if args.tags:
        cmd += " --tags"
    if args.heads:
        cmd += " origin +refs/heads/*:refs/remotes/origin/*"


    paths = subcommands.Repo.get_repo_clone_paths(repo_data)
    return executor.run_in_repos(paths, cmd)