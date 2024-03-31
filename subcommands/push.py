#!/usr/bin/python

"""
Module for handling the mgit push command, which can be used to push references upstream in multiple repos
"""
import subcommands
from subcommands import executor
from collections import defaultdict
import logging
import json

logger = logging.getLogger(__name__)

def parse_args(parser):
    """ Argument parsing for the push command """
    parser.add_argument('--tags', action='store_true',
                        help="Push all tags to the upstream repostory")
    parser.add_argument('--delete', action='store_true',
                        help="Delete the specified branch/tag in the upstream repository")
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help="Don't push anything, only display what would be pushed")
    parser.add_argument('-f', '--force', action='store_true',
                        help="Force push the branch/tag even if there are errors")
    parser.add_argument('upstream', nargs='?',
                        help="The name of the remote repository to push to")
    parser.add_argument('source', nargs='*', metavar='branch_or_tag',
                        help="The branch or tag to be pushed")
    parser.set_defaults(func=run)


def populate_repo_sources(repo_sources, repos, source):
    """ Populates source list for each repository"""
    for repo in repos:
        repo_sources[repo].append(source)


def run(args, repo_data):
    """ Main function for the push command """
    repos = subcommands.Repo.get_repo_clone_paths(repo_data)

    cmd = "git push"
    if args.tags:
        cmd += " --tags"
    if args.delete:
        cmd += " --delete"
    if args.dry_run:
        cmd += " --dry-run"
    if args.force:
        cmd += " --force"
    if args.upstream:
        cmd += f" {args.upstream}"
        logging.debug(args)
        if args.source:
            # builds individual commands for each repo based on which branches/tags it contains
            cmd += " {}"
            # specialized dictionary implementation that allows you to set a default value for keys that have not been set yet
            repo_sources = defaultdict(list)
            for source in args.source:
                ref = source.partition(':')[0]
                tag_repos = subcommands.utils.lookup_tag_or_branch(repos, ref, 'tag')
                if tag_repos:
                    populate_repo_sources(repo_sources, tag_repos, source)
                else:
                    branch_repos = subcommands.utils.lookup_tag_or_branch(repos, ref, 'branch',
                                                                          allow_remote_ref=False, check_origin=False)
                    populate_repo_sources(repo_sources, branch_repos, source)
                    if not branch_repos:
                        logger.error(f"Reference {ref} is not a valid tag or branch in any repo")
                        return False
            logger.debug(f"Repos and Sources: {json.dumps(repo_sources, indent = 4)}")
            repo_sources = {repo: " ".join(source_list) for repo, source_list in repo_sources.items()}
            return executor.run_in_repos(list(repo_sources.keys()), cmd, list(repo_sources.values()))
    return executor.run_in_repos(repos, cmd)