#!/usr/bin/python

"""
Module for handling the mgit list command, which prints out the list of repos related info
"""
import subcommands
from subcommands import executor
import argparse
import logging

logger = logging.getLogger(__name__)

def parse_args(parser):
    """ Argument parsing for the list command """
    output_parser = parser.add_mutually_exclusive_group()
    output_parser.add_argument('--url', action='store_true', help="Output just the URL of the repo")
    output_parser.add_argument('--dest', action='store_true', help="Output just the destination")
    parser.add_argument('--gitrefs-path', action='store_true',
                        help="Output just the gitrefs path configured for a product")
    parser.add_argument('--skip-build-repo', action='store_true',
                        help="Output just the repos for which skip_build is configured - NO USE")
    parser.add_argument('--get-config-file-path', action='store_true',
                        help="Extract repo path where config file is present - NO USE")
    parser.add_argument('--filter-success', action='append', default=[],
                        help="Return only repos that return successfully from the specified command")
    parser.add_argument('--filter-failure', action='append', default=[],
                        help="Return only repos that return unsuccessfully from the specified command")
    parser.set_defaults(func=run)


def filter_repos(repos, filter_cmd, success):
    """ Filter the set of repos based on ones that succeed/fail a particular command """
    data = executor.get_data_from_repos(repos, filter_cmd)
    filtered_repos = set()
    for repo, code in data['returncode'].items():
        if (code == 0) == success:
            filtered_repos.add(repo)
    return list(filtered_repos)


def run(args, repo_data):
    """ Main function for the list command """
    if args.gitrefs_path and not args.include_gitrefs:
        raise argparse.ArgumentTypeError("--gitrefs-path requires --include-gitrefs to be provided")

    if not args.skip_build_repo:
        logger.debug("Checking if any skip_build key is present in schema")
        skip_build_repo_data = []
        for repo in repo_data:
            skip_build_repo_data.append(repo)
        repo_data = skip_build_repo_data

    repos = subcommands.Repo.get_repo_clone_paths(repo_data)
    if args.get_config_file_path:
        for repo in repo_data:
            if repo.config_file_repo:
                logger.debug(f"Config file repo: {repo.config_file_repo}")
                print(repo.config_file_repo)
                return True
        return False

    filter = True if args.filter_success else False if args.filter_failure else None
    for cmd in args.filter_success + args.filter_failure:
        repos = filter_repos(repos, cmd, filter)
    
    result = set()
    for repo in repo_data:
        if args.url:
            if repo.dest in repos:
                logger.debug("Enabled '--url' in main command")
                result.add(f"{args.config['server']}{repo.repo}")
        if not args.include_gitrefs:
                logger.debug("Disabled 'include-gitrefs' in main command")
        elif args.gitrefs_path and repo.gitrefs_path:
            logger.debug("Enabled 'include-gitrefs' in main command")
            result.add(repo.gitrefs_path)
        if not args.url and not args.gitrefs_path:
            logger.debug(f"Getting default output for 'list' command")
            result.add(f"{args.config['server']}:{repo.repo} {repo.dest}")
    if args.dest:
        logger.debug("Enabled '--dest' in main command")
        result = repos

    if result:
        print("\n".join(result))
        return True
    return False