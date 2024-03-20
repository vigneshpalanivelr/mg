#!/usr/bin/python

"""
Module for executing git commands in multiple repos and return the results
"""
import subprocess
import logging
import os
import sys
import termcolor
import threading
import shlex
from datetime import datetime
from tabulate import tabulate


class outputFormatter():
    """
    Displays results from command run if it is connected TTY
    """
    def __init__(self):
        # "{Part1:}[{:Part2^{width}}]".format("LeftAlignedText", "CenteredText", width=20)
        self.format_string = "{:100}[{:^{width}}]"
        # Check if the termincal is connected to termial
        terminal = sys.stdout.isatty()
        
        self.ok_string = termcolor.colored('OK', 'green') if terminal else 'OK'
        self.fail_string = termcolor.colored('FAIL', 'red') if terminal else 'FAIL'
        self.error_string = termcolor.colored('ERROR', 'red') if terminal else 'ERROR'
        self.display_width = 15 if terminal else 6

    def format_result(self, message, success):
        """ Return the message and a success or failure result """
        result = self.ok_string if success else self.fail_string
        return self.format_string.format(message, result, width=self.display_width)

    def format_error(self, message):
        """ Return the message and an error result """
        return self.format_string.format(message, self.error_string, width=self.display_width)


def remove_non_ascii(text):
    """ Remove non-ascii characters in the result """
    return ''.join([i if ord(i) < 128 else ' ' for i in text])


class RepoThread(threading.Thread):
    """ Thread class for running a single repo command and reporting the result """
    lock = threading.Lock()
    def __init__(self, repo, command, thread_timing, print_result, change_dir):
        threading.Thread.__init__(self)
        self.repo = repo
        self.cwd = self.repo if change_dir else os.getcwd()
        self.command = command
        self.thread_timing = thread_timing
        self.output = None
        self.stderr = None
        self.returncode = None
        self.print_result = print_result

    def run(self):
        """ Executes the command in the repo """
        try:
            start_time = datetime.now()
            logger.debug(f"Running CMD in {self.repo}: {' '.join(self.command)}")
            result = subprocess.run(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    universal_newlines=True, encoding='utf-8', cwd=self.cwd)
            self.output = result.stdout
            self.stderr = result.stderr
            self.returncode = result.returncode
            status = "Success" if not self.returncode else "Fail"
        except subprocess.CalledProcessError as exc:
            self.output = exc.output
            self.stderr = exc.stderr
            self.returncode = exc.returncode
            status = "Success" if not self.returncode else "Fail"
            result_string = FORMATTER.format_error(f"Executing in {self.repo}... ")
        except Exception as exc:
            result_string = FORMATTER.format_error(f"Executing in {self.repo}... ")
            self.stderr = str(exc)
            status = "Success" if not self.returncode else "Fail"
        else:
            result_string = FORMATTER.format_result(f"Executing in {self.repo}... ", (self.returncode == 0))
            status = "Success" if not self.returncode else "Fail"
        finally:
            out, err, strfmt = None, None, '%Y-%m-%d %H:%M:%S'
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            if self.print_result:
                if self.output:
                    out = remove_non_ascii(self.output.rstrip('\n'))
                if self.stderr:
                    err = self.stderr.rstrip('\n')
            else:
                result_string = None
            
            with RepoThread.lock:
                display_results(self.command, self.cwd, result_string, out, err)
                self.thread_timing.append([self.repo, start_time.strftime(strfmt), end_time.strftime(strfmt), total_time, status])


logger = logging.getLogger(__name__)
FORMATTER = outputFormatter()
QUIET = False
IGNORE_MISSING = False


def display_results(cmd, repo, info, out, err):
    """
    Display results from GIT Command execution
    """
    if not QUIET and info:
        print(info)
    if os.getenv("DEBUG"):
        print(f"Ran in repo {repo}: {cmd}")
    if out:
        print(out)
    if err:
        print(err, file=sys.stderr)  # Enabling CLI to redirect stderr
    if not QUIET and (out or err):
        print()


def run(cmd, message, cwd=None, show_successful_output=True):
    """
    Run git command and display results in formatted output
    """
    success, out, err = True, None, None
    try:
        res = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             check=True, universal_newlines=True)
    except subprocess.CalledProcessError as exc:
        result_string = FORMATTER.format_result(f"{message}", False)
        logger.error(f"FAILED: {message}")
        if exc.stdout:
            out = exc.stdout
        err = str(exc).rstrip('\n')
        success = False
    except Exception as exc:
        result_string = FORMATTER.format_result(f"{message}", False)
        logger.error(f"FAILED: {message}")
        out = ""
        err = str(exc).rstrip('\n')
        success = False       
    else:
        result_string = FORMATTER.format_result(f"{message}", True)
        if show_successful_output and res.stdout:
            out = res.stdout.rstrip('\n')
        if res.stderr:
            err = res.stderr.rstrip('\n')
    finally:
        display_results(cmd, cwd, result_string, out, err)
    return success


def get_dynamic_args(repos, *args):
    """
    repos: List of repo destination dir
    *args: List of List with branch, url, dest
    Returns: List of list [[repo1], [repo2], []]
    """
    repo_args = [[] for x in range(len(repos))]
    for arg in args:
        if not hasattr(arg, '__iter__') or len(repos) != len(arg):
            raise ValueError(f"An argument {arg} is not a list of the correct length as {repos}")
        for repo_num in range(len(repos)):
            repo_args[repo_num].append(arg[repo_num])
    return repo_args


def run_in_repos(repos, cmd, *args, parallel=True, change_dir=True, delay=None):
    """
        Run git command in the provided repos and display result for each repo.
        If additional args are provided, they must be a list of the same size as repos.
        These additional args will be formatted into the command to run for each repo.
        This allows the caller to choose slightly different commands to run in each repo.
    """
    result, threads = True, []
    thread_timing = []
    logger.debug(f"Parallel execution is: {parallel}")

    repo_args = get_dynamic_args(repos, *args)
    logger.debug(f"Structured args: {repo_args}")

    for repo_num, repo in enumerate(repos):
        # Content of list of list "*repo_args[repo_num]" and do string formatting
        torun = cmd.format(*repo_args[repo_num])

        if change_dir and not os.path.isdir(repo):
            # Ignore the fact that this workspace has not been cloned
            logger.warn("Ignore if the repos in workspace has not been cloned")
            continue

        if parallel:
            thread = RepoThread(repo, shlex.split(torun), thread_timing, True, change_dir)
            threads.append(thread)
            thread.start()
            if delay is not None:
                time.sleep(delay)
        else:
            result &= run(torun, f"Executing in {repo}...", cwd=repo if change_dir else os.getcwd())

    for thread in threads:
        thread.join()
        result &= (thread.returncode == 0)

    if not result and not QUIET:
        logger.error("Operation failed in some repo(s). Check details above.")
    
    print()
    print(tabulate(thread_timing, headers=["Thread", "Start Time", "End Time", "Total Time (s)", "Status"], tablefmt="psql"))
    return result


def get_data_from_repos(repos, cmd, *args, parallel=True, change_dir=True, delay=None, data=True):
    """
        Run git command in the provided repos and display result for each repo.
        If additional args are provided, they must be a list of the same size as repos.
        These additional args will be formatted into the command to run for each repo.
        This allows the caller to choose slightly different commands to run in each repo.
    """
    result, threads = True, []
    thread_timing = []
    result = {'returncode': dict(), 'output': dict(), 'stderr': dict()}
    logger.debug(f"Parallel execution is: {parallel}")

    repo_args = get_dynamic_args(repos, *args)
    logger.debug(f"Structured args: {repo_args}")

    for repo_num, repo in enumerate(repos):
        # Get content of list "*repo_args[repo_num]" and do string formatting
        torun = cmd.format(*repo_args[repo_num])
        
        if change_dir and not os.path.isdir(repo) and IGNORE_MISSING:
            # Ignore the fact that this workspace has not been cloned
            logger.warn("Ignore if the repos in workspace has not been cloned")
            continue
        
        if parallel:
            thread = RepoThread(repo, shlex.split(torun), thread_timing, True, change_dir)
            threads.append(thread)
            thread.start()
            if delay is not None:
                time.sleep(delay)
        else:
            result &= run(torun, f"Executing in {repo}...", cwd=repo if change_dir else os.getcwd())

    for thread in threads:
        thread.join()
        if data:
            result['returncode'][thread.repo] = thread.returncode
            result['output'][thread.repo] = thread.output
            result['stderr'][thread.repo] = thread.stderr
        else:
            result &= (thread.returncode == 0)

    if not result and not QUIET:
        logger.error("Operation failed in some repo(s). Check details above.")
    if not data:
        print()
        print(tabulate(thread_timing, headers=["Thread", "Start Time", "End Time", "Total Time (s)", "Status"], tablefmt="psql"))
    return result


def run_repo_cmds(cmds, step):
    """ Runs all commands specified for repos from .mgit.yaml files """
    for repo in cmds.keys():
        logger.debug(f"Running {step} steps in {repo}:")
        for cmd in cmds[repo]:
            repo_dir = os.path.join(os.getcwd(), repo)
            run(shlex.split(cmd), f'Executing {cmd}', cwd=repo_dir)
