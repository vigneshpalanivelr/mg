#!/usr/bin/env svtoolspython

"""
Module for handling the mgit tag command, which can be used to list, create, or delete tags in multiple repos
"""

import sys

from subcommands import executor
import subcommands
import logging


logger = logging.getLogger(__name__)

def parse_args(parser):
    """ Argument parsing for the tag command """
    parser.add_argument('-a', '--annotate', action='store_true',
                        help="Make an annotated tag object")
    parser.add_argument('-m', '--message', nargs=1,
                        help="Use the given tag message")
    parser.add_argument('-f', '--force', action='store_true',
                        help="Force creation of a tag, even if it already exists")
    parser.add_argument('-d', '--delete', metavar='tag', nargs='*',
                        help="Delete the specified tag names")
    parser.add_argument('-l', '--list', metavar='REGEX-PATTERN',
                        help="List tags with names that match the given regex pattern")
    parser.add_argument('--sort', choices= ('authordate', 'creatordate', 'committerdate', 'refname', 'taggerdate'),
                        help="Sort in a specific order")
    parser.add_argument('tag', nargs='?',
                        help="Name of the tag to create")
    parser.add_argument('source', nargs='?', metavar='branch_or_tag',
                        help="Starting point branch or tag from which to create the tag")
    parser.set_defaults(func=run)


def run(args, repo_data):
    """ Main function for the tag command """
    repos = subcommands.Repo.get_repo_clone_paths(repo_data)
    cmd = "git tag"
    if args.annotate:
        cmd += " -a"
    if args.message:
        cmd += f" -m '{args.message[0]}'"
    if args.list:
        cmd += f" -l '{args.list}'"
    if args.sort:
        cmd += f" --sort '{args.sort}'"
    if args.force:
        cmd += " -f"
    if args.delete:
        tags = ' '.join(args.delete)
        exit = False
        cmd += f" -d {tags}"
        if args.annotate:
            logger.error(f"Unexpected argument: '-a'")
            exit = True
        if args.message:
            logger.error(f"Unexpected argument: '-m'")
            exit = True
        if args.tag:
            logger.error(f"Unexpected argument: tag")
            exit = True
        if exit:
            return False
    if args.tag:
        cmd += f" {args.tag}"
    if args.source:
        cmd += " {}"
        return subcommands.utils.run_command_for_tag_or_branch(repos, repo_data, cmd, args.source)
    return executor.run_in_repos(repos, cmd)
    
