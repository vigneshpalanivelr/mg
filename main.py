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
    parser = argparse.ArgumentParser(description='Git Operations across multiple repos')
    parser.add_argument('--config-file', default=os.path.join(sys.path[0], 'mg.yaml'),
                        help="Override default location of yaml config file")
    parser.add_argument('--multigit-dir', default='.multigit', help="Products directory to get repos")
    parser.add_argument('--quiet', action='store_true', default=False, help="Suppress the git command execution")
    parser.add_argument('--sync', action='store_true', default=False, help="Synchronize the local schema path")
    parser.add_argument('--verbose', action='store_true', default=False, help="Enable DEBUG logging for the script")
    product_group = parser.add_mutually_exclusive_group()
    product_group.add_argument('--product-file',
                              help="Provide product file for repo information")
    product_group.add_argument('--product-path',
                              help="Provide product directory for storing product files")

    return parser.parse_args()


def main():
    """
    Main entry point into the script
    """
    args = parse_args()

    log_level = logging.DEBUG
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
    
    # Supress the git command
    subcommands.executor.QUIET = args.quiet
    logging.debug(f"Suppress git command output and display only final result: {subcommands.executor.QUIET}")

    # Get MultiGit directory
    if not args.product_file and not args.product_path:
        subcommands.utils.find_mgit(args.multigit_dir)

    product_data = subcommands.utils.get_product_data(args.product_file, args.product_path, args.multigit_dir,
                                                      args.config, args.sync)
           




if __name__ == '__main__':
    main()