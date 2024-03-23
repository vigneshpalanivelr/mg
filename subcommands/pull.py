#!/usr/bin/python

"""
Module for handling the mgit pull command, which can be used to fetch and merge branches in multiple repos
"""
from subcommands import executor
import subcommands


def parse_args(parser):
    """ Argument parsing for the pull command """
    parser.add_argument('--depth',
                        help="pull a history truncated to the specified number of revisions")
    parser.add_argument('--recurse-submodules', dest='recursive', action='store_true',
                        help="Recursively pull all submodules within, using their default settings")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--ff', action='store_true',
                       help="Allow only fast-forward merges; equivalent to --ff-only")
    group.add_argument('--no-ff', action='store_true',
                       help="Create a merge commit even when the merge resolves as a fast-forward")
    group.add_argument('--ff-only', action='store_true',
                       help="Refuse to merge unless the merge can be resolved as fast-forward")
    parser.add_argument('--rebase', action='store_true',
                        help="Rebase instead of creating a merge commit")
    parser.add_argument('upstream', nargs='?',
                        help="Pull from the specified upstream repository")
    parser.add_argument('source', nargs='?', metavar='branch_or_tag',
                        help="Merge the specified branch or tag into the current branch")
    parser.set_defaults(func=run)


def run(args, repo_data):
    """ Main function for the pull command """
    repos = subcommands.Repo.get_repo_clone_paths(repo_data)

    cmd = "git pull"
    if args.depth:
        cmd += f" --depth {args.depth}"
    if args.recursive:
        cmd += " --recurse-submodules"
    if args.rebase:
        cmd += " --rebase"
    if args.ff_only:
        cmd += " --ff-only"
    elif args.no_ff:
        cmd += " --no-ff"
    elif args.ff:
        cmd += " --ff"
    if args.upstream:
        cmd += f" {args.upstream}"
        if args.source:
            cmd += f" {args.source}"
    return executor.run_in_repos(repos, cmd)