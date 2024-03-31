#!/usr/bin/python

"""
Module for handling the mgit branch command, which can be used to list, create, delete or rename branches
"""

import sys
from subcommands import executor
import subcommands
import logging
import json

logger = logging.getLogger(__name__)


def parse_args(parser):
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument('-a', '--all', action='store_true',
                              help="Show all branches, including remotes")
    action_group.add_argument('--current', action='store_true',
                              help="Show currently checkout branch")
    action_group.add_argument('-r', '--remotes', action='store_true',
                              help="Show remote branches")
    action_group.add_argument('-d', '--delete', metavar='branch', nargs='*',
                              help="Delete the specified branch(es), provided they are fully merged upstream")
    action_group.add_argument('-D', dest='force_delete', metavar='branch', nargs='*',
                              help="Delete the specified branch(es), regardless whether they are fully merged upstream"
                              " or not")
    action_group.add_argument('--delete-pattern', metavar='branch',
                              help="Delete all branches matching the given glob pattern, except if it is checked out")
    action_group.add_argument('-m', '--move', metavar='branch', nargs=2,
                              help="Move/rename a branch")
    action_group.add_argument('-M', dest='force_move', metavar='branch', nargs=2,
                              help="Move/rename a branch, even if the new branch name already exists")
    action_group.add_argument('--unset-upstream', metavar='branch', nargs=1,
                              help="Unset the specified branch's upstream branch")
    parser.add_argument('-u', '--set-upstream-to', metavar='upstream',
                        help="Set up the branch's tracking information to the specified upstream branch")
    track_group = parser.add_mutually_exclusive_group()
    track_group.add_argument('-t', '--track', action="store_true",
                             help="Set up configuration to mark the start-point branch as upstream from the new"
                             " branch")
    track_group.add_argument('--no-track', dest='track', action="store_false",
                             help="Do not set up configuration to mark the start-point branch as upstream from the new"
                             " branch")
    parser.set_defaults(track=False)
    parser.add_argument('-f', '--force', action='store_true',
                        help="Force creation of a branch, even if it already exists or the source does not exist")
    parser.add_argument('branch', nargs='?',
                        help="Name of the branch to create")
    parser.add_argument('source', nargs='?', metavar='branch_or_tag',
                        help="Branch or tag to use as a starting point when creating the branch")
    parser.set_defaults(func=run)


def validate_args(args):
    """ Validate that no inconsistent arguments were used together """
    action = 'create'
    if args.delete or args.force_delete or args.delete_pattern:
        action = 'delete'
    if args.move or args.force_move:
        action = 'move'
    if args.unset_upstream:
        action = 'unset_upstream'
    if args.all or args.remotes:
        action = 'list'
    if args.current:
        action = 'current'

    success = True
    if action != 'create':
        if args.branch:
            logger.error(f"Unexpected argument: {args.branch}")
            success = False
        if args.source:
            logger.error(f"Unexpected argument: {args.source}")
            success = False
        if args.set_upstream_to:
            logger.error(f"The --set-upstream-to/-u argument is inconsistent with the {action} action")
            success = False
        if args.track:
            print(f"The --track/-t argument is inconsistent with the {action} action", file=sys.stderr)
            success = False
    if not success:
        return False
    return True


def get_passthru_args(args):  # noqa: C901
    """ Concatenate the pass-through arguments and return them as a string """
    result = ""
    if args.all:
        result += " -a"
    elif args.remotes:
        result += " -r"
    elif args.delete:
        branches = " ".join(args.delete)
        result += f" -d {branches}"
    elif args.force_delete:
        branches = " ".join(args.force_delete)
        result += f" -D {branches}"
    elif args.delete_pattern:
        result += " -D {}"
    elif args.move:
        branches = " ".join(args.move)
        result += f" -m {branches}"
    elif args.force_move:
        branches = " ".join(args.force_move)
        result += f" -M {branches}"
    elif args.unset_upstream:
        branches = " ".join(args.unset_upstream)
        result += f" --unset-upstream {branches}"

    if args.force:
        result += " -f"
    if args.set_upstream_to:
        result += f" -u {args.set_upstream_to}"
    if args.track:
        result += " --track"
    if args.branch:
        result += f" {args.branch}"

    return result


def run(args, repo_data):
    """ Main function for the branch command """
    repos = subcommands.Repo.get_repo_clone_paths(repo_data)
    if not validate_args(args):
        return False

    cmd = "git branch {}".format(get_passthru_args(args))

    if args.source:
        cmd += " {}"
        return subcommands.utils.run_command_for_tag_or_branch(repos, repo_data, cmd, args.source, force=args.force)

    if args.current:
        cmd = "git symbolic-ref HEAD"
    
    if args.delete_pattern:
        find_brs = f"git for-each-ref --format \'%(refname:short)\' refs/heads/{args.delete_pattern}"
        data_dict = executor.get_data_from_repos(repos, find_brs)
        logger.debug(json.dumps(data_dict, sort_keys=True, indent=4, separators=(',', ': ')))
        matching_branches = {k: " ".join(v.rstrip('\n').split('\n'))
                             for k, v in data_dict['output'].items()
                             if v.rstrip('\n') != ''}
        logger.debug(json.dumps(matching_branches, sort_keys=True, indent=4, separators=(',', ': ')))
        return executor.run_in_repos(list(matching_branches.keys()), cmd, list(matching_branches.values()))
    return executor.run_in_repos(repos, cmd)