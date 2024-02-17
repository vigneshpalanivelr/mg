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
    parser.add_argument('--quiet', action='store_true', default=False,
                        help="Suppress the git command and execution details, disply only output from git")
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
    formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                        format=formatter, datefmt="%Y-%m-%d %H:%M:%S")
    logging.debug(args)

    # Read the config file
    args.config = subcommands.utils.get_config(args.config_file)
    # Exit if the config file is empty
    if not args.config:
        logging.exception("Config file is Empty")
    
    # Supress the git command
    subcommands.executor.QUIET = args.quiet
    logging.debug(f"Suppress git command output and display only final result: {subcommands.executor.QUIET}")

    # Check Product File and Product Path
    if not args.product_file and not args.product_path:
        




if __name__ == '__main__':
    main()