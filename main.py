#!/usr/bin/python

"""
MultiGit is a tool for operating on multiple git repos together as one
"""
import argparse
import os
import sys
import logging

import subcommands


def parse_args():
    """
    Parse command line arguments to the script
    """
    def list_str(values):
        return values.split(',')
    
    parser = argparse.ArgumentParser(description='Git Operations across multiple repos')
    parser.add_argument('--config-file', default=os.path.join(sys.path[0], 'mgit.yaml'),
                        help="Override default location of yaml config file")
    parser.add_argument('--multigit-dir', default='.multigit', help="schema directory to get repos")
    parser.add_argument('--quiet', action='store_true', default=False, help="Suppress the git command execution")
    parser.add_argument('--sync', action='store_true', default=False, help="Synchronize the local schema path")
    parser.add_argument('--verbose', action='store_true', default=False, help="Enable DEBUG logging for the script")
    parser.add_argument('--schema-branch', default='next/develop', help="Branch for the schema repo to work with")
    #parser.add_argument('--schema-branch', help="schema directory to get repos")
    parser.add_argument('--products', default=[], type=list_str, help="Limit operations to repos related to the specified product(s) (comma-separated str)")
    parser.add_argument('--repos', default=[], type=list_str, help="Limit operations to the specified repo clone path(s) (comma-separated str)")
    parser.add_argument('--repo-urls', default=[], type=list_str, help="Limit operations to the specified repo url(s)(comma-separated str)")
    parser.add_argument('--require-all', action='store_true', help="Attempt to run in all repos defined by the schema and fail if any workspace is missing.")

    schema_group = parser.add_mutually_exclusive_group()
    schema_group.add_argument('--schema-file', help="Provide schema file for repo information")
    schema_group.add_argument('--schema-path', help="Provide schema directory for cloning schema repo")

    subparsers = parser.add_subparsers(dest="command", help="sub-command help")
    subparsers.add_parser('init').set_defaults(func = subcommands.init.run)
    subcommands.clone.parse_args(subparsers.add_parser('clone'))
    return parser.parse_args()


def main():
    """
    Main entry point into the script
    """
    args = parse_args()

    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG
    formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(stream=sys.stdout, level=log_level, format=formatter, datefmt="%Y-%m-%d %H:%M:%S")
    logging.debug(args)

    # Read the config file
    args.config = subcommands.utils.get_config(args.config_file)
    # Exit if the config file is empty
    if not args.config:
        logging.exception("Config file is Empty")
        sys.exit(2)
    
    # Supress the git command
    subcommands.executor.QUIET = args.quiet
    logging.debug(f"Suppress git command output and display only final result: {subcommands.executor.QUIET}")

    # Find MultiGit directory
    if not args.schema_file and not args.schema_path:
        subcommands.utils.find_mgit(args.multigit_dir)
    
    # Read all the schema data and Exit if schema data is not present
    schema_data = subcommands.utils.get_schema_data(args.schema_file, args.schema_path, args.multigit_dir,
                                                    args.config, args.schema_branch, args.sync)
    if not schema_data:
        logging.error("Couldn't load schema, try updating schema using --sync option")
        sys.exit(3)
    
    # Read repository data from schema
    repo_data = subcommands.Repo.get_repo_data(schema_data, args.products, args.repos, args.repo_urls)
    if not repo_data:
        logging.error(f"No schema defined for the product: {args.products} or product not matched")
        sys.exit(4)
    logging.debug(f"Successfully loaded schema data")
    subcommands.executor.IGNORE_MISSING = (not args.require_all)

    # Execute commands
    if args.func(args, repo_data):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()