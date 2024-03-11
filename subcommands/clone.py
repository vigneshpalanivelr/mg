#!/usr/bin/python

"""
Module for handling the mgit clone command, which can be used to clone multiple repos
"""

import os
import subcommands
from subcommands import executor
import logging


logger = logging.getLogger(__name__)


def parse_args(parser):
    """ Argument parsing for the clone command """
    parser.add_argument('--depth',
                        help="Create a shallow clone with a history truncated to the specified number of revisions")
    parser.add_argument('--recursive', action='store_true',
                        help="After clone, initialize all submodules with their default settings")
    parser.add_argument('--no-checkout', '-n', action='store_true',
                        help="Don't checkout HEAD after cloning")
    parser.add_argument('--branch',
                        help="Checkout the provided branch, or the longest-prefix matching branch")
    parser.add_argument('--missing', action='store_true',
                        help="Only clone missing repositories and ignore already-cloned repos")
    parser.set_defaults(func=run)


def run(args, repo_data):
    """ Main function for the clone command """
    server = args.config['server']

    clone_cmd = "git clone"
    clone_cmd += f" --depth {args.depth}" if args.depth else ""
    clone_cmd += " --recursive" if args.recursive else ""
    clone_cmd += " --no-checkout" if args.no_checkout else ""
    clone_cmd += f" --branch {{}} {server}{{}} {{}}"

    # Prepare list of repos to clone
    repos_to_clone = {repo.dest: repo for repo in repo_data if not args.missing or not os.path.isdir(repo.dest)}
    repo_list = repos_to_clone.values()
    url_arg = [x.repo for x in repo_list]
    dest_arg = [x.dest for x in repo_list]
    checkout_dest_arg = [x.dest for x in repo_data]
    
    # Find long-prefix-matahced branch for each repo
    branch_info = subcommands.utils.find_lpm_branch_from_url(server, repo_list, args.branch)
    branch_arg = [branch_info[x.repo] for x in repo_list]

    # Run clone command
    result = executor.run_in_repos(dest_arg, clone_cmd, branch_arg, url_arg, dest_arg, change_dir=False)

    # In-complete
    for repo in repo_data:
        repo.create_link()

    post_clone_cmds = subcommands.utils.get_repo_config(repo_data, 'post_clone')
    subcommands.executor.run_repo_cmds(post_clone_cmds, 'post_clone')

    return result