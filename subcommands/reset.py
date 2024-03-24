#!/usr/bin/python

"""
Module for handling the mgit reset command, which sets the HEAD, working tree and/or index to a particular commit
"""

import os
from subcommands import executor
import subcommands


def parse_args(parser):
    """ Argument parsing for the rebase command """
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--soft', dest='mode', action='store_const', const='soft',
                       help="Do not touch the index file nor the working tree at all")
    group.add_argument('--mixed', dest='mode', action='store_const', const='mixed',
                       help="Reset the index but not the working tree (this is the default)")
    group.add_argument('--hard', dest='mode', action='store_const', const='hard',
                       help="Reset the index and the working tree")
    parser.set_defaults(mode='mixed')
    parser.add_argument('--sparse-paths',
                        help="Check out only the paths that are specified in comma-separated")
    parser.add_argument('--rw-repos',
                        help="Enforce sparse checkout in these repos only")
    parser.add_argument('source', nargs='?', metavar='branch_or_tag',
                        help="The name of the branch or tag to reset to")
    parser.add_argument('--force', action='store_true',
                        help="Force option to reset the branch")
    parser.set_defaults(func=run)


def run(args, repo_data):
    """ Main function for the reset command """
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

    cmd = f"git reset --{args.mode}"

    if args.source:
        cmd += " {}"
        logger.debug("Sparse Checkout is configured")
        return subcommands.utils.run_command_for_tag_or_branch(repos, repo_data, cmd, args.source, False, args.force)

    logger.debug("Sparse Checkout is not configured")
    return executor.run_in_repos(repos, cmd)