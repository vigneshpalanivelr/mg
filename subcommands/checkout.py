#!/usr/bin/python

"""
Module for handling the mgit checkout command, which can be used to checkout a branch to multiple repos
"""


import os
import sys
import subcommands
from subcommands import executor
import logging


logger = logging.getLogger(__name__)

def parse_args(parser):
    """ Argument parsing for the checkout command """
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-b', dest='new_branch', metavar='new_branch',
                       help="Create new_branch if it doesn't exist, using the source argument as a starting point")
    group.add_argument('-B', dest='new_branch_force', metavar='new_branch',
                       help="Create or overwrite new_branch, using the source argument as a starting point")
    parser.add_argument('--force', action='store_true',
                        help="Force option to checkout the parent branch if the branch doesn't exist")
    group.add_argument('--orphan', metavar='new_branch',
                       help="Create a new orphan branch new_branch, with no history")
    parser.add_argument('--sparse-paths',
                        help="Check out only the paths that are specified in comma-separated")
    parser.add_argument('--rw-repos',
                        help="Enforce sparse checkout in these repos only")
    parser.add_argument('source', nargs='?',
                        help="The name of the branch or tag to check out, or starting point to create from")
    parser.set_defaults(func=run)


def run(args, repo_data):
    repos = subcommands.Repo.get_repo_clone_paths(repo_data)
    if args.rw_repos:
        repos = list(set(repos) & set(args.rw_repos.split(',')))
        logger.debug(f"Sparsh checkout enabled repos: {', '.join(repos)}")
    
    if args.sparse_paths:
        paths = "\n".join(args.sparse_paths.split(','))
        logger.debug(f"Sparsh Paths: {paths}")
        for repo in repos:
            sparsh_file = os.path.join(repo, '.git', 'info', 'sparse-checkout')
            logger.debug(f"Creating and Updating sparsh paths: {sparsh_file}")
            with open(sparsh_file, "w+") as file:
                file.write(paths)
        cmd = "git config core.sparseCheckout true"
        executor.get_data_from_repos(repos, cmd)

    cmd = "git checkout"
    if args.new_branch:
        cmd += f" -b {args.new_branch}"
    elif args.new_branch_force:
        cmd += f" -B {args.new_branch_force}"
    elif args.orphan:
        cmd += f" --orphan {args.orphan}"

    if not args.source:
        logger.debug("Sparse Checkout is not configured")
        if not args.new_branch and not args.new_branch_force and not args.orphan:
            logger.error("You must provide a new branch to create or a source to checkout.")
            return False
        return executor.run_in_repos(repos, cmd)

    cmd += " {}"
    logger.debug("Sparse Checkout is configured")
    return subcommands.utils.run_command_for_tag_or_branch(repos, repo_data, cmd, args.source, True, args.force)
