#!/usr/bin/python

"""
Restoring remote configuration for the local repos
"""
from subcommands import executor


def parse_args(parser):
    """ Argument parsing for the remote command """
    parser.add_argument('command', choices=['fix'], help="The remote sub-command to execute")
    parser.set_defaults(func=run)


def run(args, repo_data):
    """ Main function for the remote command """
    repos_to_fix = {repo.dest: repo.repo for repo in repo_data}

    cmd = f"git config remote.origin.url {args.config['server']}{{}}"
    result = executor.run_in_repos(list(repos_to_fix.keys()), cmd, list(repos_to_fix.values()))
    if result:
        cmd = f"git config remote.origin.fetch +refs/heads/*:refs/remotes/origin/*"
        result = executor.run_in_repos(list(repos_to_fix.keys()), cmd)

    return result
