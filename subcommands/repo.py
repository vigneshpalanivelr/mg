#!/usr/bin/python

"""
Module for working with repo data
"""
import os


class Repo():
    """
    Class for reading Product repo and path
    """
    def __init__(self, schema_dict):
        self.repo = schema_dict['repo']
        self.dest = schema_dict['path']
        self.version = schema_dict['ref']
        self.symlink, self.submodule, self.lfs = None, False, False
        self.gitrefs_path, self.skip_build, self.config_file_repo = None, False, None
        if 'symlink' in schema_dict:
            self.symlink = schema_dict['symlink']
        if 'enable_submodule' in schema_dict:
            self.submodule = True
        if 'lfs_fetch' in schema_dict:
            self.lfs = True
        if 'gitrefs_path' in schema_dict:
            self.gitrefs_path = schema_dict['gitrefs_path']
        if 'skip_build' in schema_dict:
            self.skip_build = True
        if 'config_file_repo' in schema_dict:
            self.config_file_repo = schema_dict['config_file_repo']


    @staticmethod
    def get_repo_data(schema_data, products=None, repos=None, repo_urls=None):
        repo_data = []
        for prod in schema_data:
            if not products or prod['product'] in products:
                for repo in prod['repos']:
                    if (not repos and not repo_urls) or repo['path'] in repos or repo["repo" in repo_urls]:
                        repo_data.append(Repo(repo))
        return repo_data

