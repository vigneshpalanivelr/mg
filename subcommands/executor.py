#!/usr/bin/python

"""
Module for executing git commands in multiple repos and return the results
"""
import subprocess
import logging
import os
import sys
import termcolor


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
        logger.info(f"Running CMD: {' '.join(cmd)}")
        res = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             check=True, universal_newlines=True)
    except subprocess.CalledProcessError as exc:
        result_string = FORMATTER.format_result(f"{message}", False)
        logger.error(f"FAILED: {message}")
        if exc.stdout:
            out = exc.stdout
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
