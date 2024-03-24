#!/usr/bin/python

"""
Module for handling the mgit clean command, which can be used to clean out non-repo files
"""

import subcommands
from subcommands import executor


def parse_args(parser):
    """ Argument parsing for the clean command """
    parser.add_argument('-d', dest='directory', action='store_true',
                        help="Remove untracked directories in addition to untracked files")
    parser.add_argument('-f', '--force', action='store_true',
                        help="Clean even if the Git configuration variable clean.requireForce is set to false")
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help="Don't actually remove anything, just show what would be done")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-x', dest='clean_ignored', action='store_true',
                       help="Remove ignored files")
    group.add_argument('-X', dest='only_ignored', action='store_true',
                       help="Remove only ignored files")
    parser.set_defaults(func=run)


def run(args, repo_data):
    """ Main function for the push command """
    repos = subcommands.Repo.get_repo_clone_paths(repo_data)
    cmd = "git clean"
    if args.directory:
        cmd += " -d"
    if args.force:
        cmd += " --force"
    if args.dry_run:
        cmd += " --dry-run"
    if args.clean_ignored:
        cmd += " -x"
    elif args.only_ignored:
        cmd += " -X"
    return executor.run_in_repos(repos, cmd)
