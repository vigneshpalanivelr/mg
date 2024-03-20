#!/usr/bin/env svtoolspython

"""
Module for handling the mgit push command, which can be used to push references upstream in multiple repos
"""
import subcommands

def parse_args(parser):
    """ Argument parsing for the push command """
    parser.add_argument('--delete', action='store_true',
                        help="Delete the specified branch/tag in the upstream repository")
    parser.add_argument('upstream', nargs='?',
                        help="The name of the remote repository to push to")
    parser.add_argument('source', nargs='*', metavar='branch_or_tag',
                        help="The branch or tag to be pushed")
    parser.set_defaults(func=run)


def run(args, repo_data):
    """ Main function for the push command """
    repos = subcommands.Repo.get_repo_clone_paths(repo_data)

    cmd = "git push"
    if args.delete:
        cmd += " --delete"
    cmd += f" {args.upstream}"
    if args.upstream:
        # builds individual commands for each repo based on which branches/tags it contains
        cmd += " {}"
        repo_sources = defaultdict(list)
        for source in args.source:
            print(source)

    return executor.run_in_repos(repos, cmd)