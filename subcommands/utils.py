#!/usr/bin/python

"""
Utility function for the mg command
"""

import yaml
import logging
import os
import re
import subprocess

from subcommands import executor

logger = logging.getLogger(__name__)

def get_config(config_file):
    """
    Parses the config file and returns it as a dict 
    """
    try:
        with open(config_file) as yaml_file:
            config = yaml.safe_load(yaml_file)
    except yaml.YAMLError as exc:
        logger.error(f"Unable to load config file {config_file}. Details:", str(exc))
        return None
    return config


def find_mgit(target_directory):
    """
    Search for .multigit directory
    """
    current_dir = os.getcwd()
    while current_dir != os.sep and current_dir != os.path.abspath(os.sep):
        if target_directory in os.listdir(current_dir):
            os.chdir(current_dir)
            logger.debug(f"Found MultiGit directory: {current_dir}")
            break
        current_dir = os.path.dirname(current_dir)
        logger.debug(f"Couldn't Find MultiGit directory in: {current_dir}")


def update_schema_repos(config, clone_dir):
    """
    Clone all the repos to the specified dir from the schema yaml file
    """
    git_server = "{}{}".format(config['server'], config['schema_path'])
    if os.path.isdir(clone_dir):
        message = f"Updating schema repo {git_server}..."
        executor.run(["git", "fetch", "origin"], message, cwd=clone_dir)
    else:
        message = f"Cloning schema repo {git_server}..."
        executor.run(["git", "clone", git_server, os.path.basename(clone_dir)], message, cwd=os.path.dirname(clone_dir))


def get_schema_contents(schema_file):
    """
    Read in the provided schema file and return the data
    """
    with open(schema_file) as file_contents:
        return yaml.safe_load(file_contents)


def find_lpm_schema_branch(schema_root, schema_branch, include_origin=True):
    """
    Find the longest-prefix-matching schema branch in the schema repo
    """
    branch_prefix = schema_branch
    single_chunk = check_develop = False

    while branch_prefix:
        if branch_prefix.startswith("refs/"):
            cmd = f"git show-ref {branch_prefix}"
        else:
            cmd = f"git show-ref refs/heads/{branch_prefix} refs/remotes/{branch_prefix}"

        if include_origin:
            cmd += f" refs/remotes/origin/{branch_prefix}"
        
        logger.debug(f"Running CMD: {cmd}")
        subprocess_data = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                         universal_newlines=True, cwd=schema_root, check=False)

        # If the prefix is found, it returns
        if subprocess_data.returncode == 0:
            logger.debug(f"Found parent branch: {branch_prefix}")
            return branch_prefix

        # If could not find any branch then break and return default
        if check_develop:
            branch_prefix = branch_prefix.split("/")[0]
            logger.warn(f"Could not find parent branch, returning default")
            break

        # If prd.26.20 then check if its parent is available in remote/local
        if single_chunk and branch_prefix not in ["origin", "next"]:
            branch_prefix = f"{branch_prefix}/develop"
            check_develop = True
            logger.warn(f"Single chunk branch name: {branch_prefix}")
            continue

        branch_prefix = ''.join(re.split('([/-])', branch_prefix)[:-2])
        single_chunk = len(re.split('([/-])', branch_prefix)) == 1
        logger.debug(f"Reducing last chunk and check: {branch_prefix}")

    return "next/develop"


def read_schema_data(schema_file):
    """
    Read in the provided schema file and return the data
    """
    with open(schema_file) as schema:
        return yaml.safe_load(schema)


# Optimized
def get_schema_files(schema_path):
    """
    Loop through each directory and read schema files
    """
    all_schema_data = []
    for path, _, files in os.walk(schema_path):
        if 'schema.yaml' in files:
            for name in files:
                if name == 'schema.yaml':
                    logger.debug(f"Reading schema data for product: {os.path.join(path, name)}")
                    all_schema_data.append(read_schema_data(os.path.join(path, name)))
    return all_schema_data


def get_schema_data(schema_file, schema_path, multigit_dir, config, schema_branch, sync=False):
    """
    Find the schema data, optionally sync it, read it in, and then return it
    """
    if schema_file:
        logger.debug(f"Loading schema details: {schema_file}")
        return [get_schema_contents(schema_file)]
    
    # Setting up .multigit directory
    if not schema_path:
        schema_path = os.path.join(os.getcwd(), multigit_dir, "schema")
        logger.debug(f"Setting-up schema path under: {schema_path}")
    
    # Clone/Fetch schema repo if sync is set
    if sync:
        logger.debug(f"Check/Create schema directory: {os.path.dirname(schema_path)}")
        os.makedirs(os.path.dirname(schema_path), exist_ok=True)
        update_schema_repos(config, schema_path)
    
    # Clean the schema branch 
    if sync and schema_branch:
        schema_branch = find_lpm_schema_branch(schema_path, schema_branch)
        executor.run(['git', 'checkout', schema_branch], f"Checking out branch {schema_branch}", cwd=schema_path)
        executor.run(['git', 'reset', "--hard", f"origin/{schema_branch}"], f"Cleaning local branch {schema_branch}", cwd=schema_path)

    if not os.path.isdir(schema_path):
        return None
    
    return get_schema_files(schema_path)


def get_ref_root(ref):
    """ Return the root of the provided ref (everything up to and excluding the last slash) """
    if ref:
        branch_root = ref.rpartition('/')[0]
        logger.debug(f"Found branch root for {ref}: {branch_root}")
        return branch_root
    return ''


def replace_root(version, new_root, add_origin=False):
    """ Replace the root of the branch with a new root from provided branch, optionally adding origin """
    default = version
    old_root = get_ref_root(version)
    if old_root:
        if new_root.startswith("origin"):
            new_root = new_root[len("origin/"):]
            add_origin = True
        if new_root:
            logger.debug(f"Old root {old_root} is replaced by new root {new_root}")
            default = version.replace(old_root, new_root)

    if add_origin and not default.startswith("origin/"):
        return f"origin/{default}"
    return default


# In-Complete
def find_lpm_branch_from_url(server, repo_data, branch, include_origin=False):
    """ Find the longest-prefix-matching branch or root tag in all repos from a remote url"""
    branch_root = get_ref_root(branch)

    # Finding default branch using pre-fix
    found_refs, default_branches = dict(), dict()
    for repo in repo_data:
        default_branches[repo.repo] = replace_root(repo.version, branch_root)
    logger.debug(f"Found default branch: {default_branches}")
    repos_remaining = list(default_branches.keys())

    if branch:
        branch_prefix = branch
        single_chunk = check_develop = False

        while repos_remaining and branch_prefix:
            logger.debug(f"Trying to find longest-prefix-matching branch: {branch_prefix}")
            if branch_prefix.startswith("refs/"):
                cmd = f"git ls-remote --exit-code {server}{{}} {branch_prefix}"
            else:
                cmd = f"git ls-remote --exit-code {server}{{}} refs/heads/{branch_prefix} refs/tags/{branch_prefix}"

            data = executor.get_data_from_repos(repos_remaining, cmd, repos_remaining, change_dir=False)
            for repo, code in data['returncode'].items():
                if code == 0:
                    found_refs[repo] = branch_prefix
                    repos_remaining.remove(repo)

            repos_remaining = []
            for repo, code in data['returncode'].items():
                if code == 0:
                    found_refs[repo] = branch_prefix
                else:
                    repos_remaining.append(repo)

            if check_develop:
                branch_prefix = branch_prefix.split("/")[0]
                break

            if single_chunk and branch_prefix not in ["origin", "next"]:
                branch_prefix = f"{branch_prefix}/develop"
                check_develop = True
                continue
            branch_prefix = ''.join(re.split('([/-])', branch_prefix)[:-2])
            single_chunk = len(re.split('([/-])', branch_prefix)) == 1

    for repo in repos_remaining:
        found_refs[repo] = default_branches[repo]
    return found_refs


def get_repo_config(repo_data, key):
    """ Gets data in key section from .mgit.yaml for all repos """
    base_dir = os.getcwd()
    data = {}
    for repo in repo_data:
        repo_path = os.path.join(base_dir, repo.dest)
        yaml_path = os.path.join(repo_path, ".mgit.yaml")
        if os.path.exists(yaml_path):
            with open(yaml_path, 'r') as fstream:
                mgit_yaml = yaml.safe_load(fstream)
            if key in mgit_yaml:
                data[repo.dest] = mgit_yaml[key]
    return data
