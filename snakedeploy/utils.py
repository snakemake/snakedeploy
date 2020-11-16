#!/usr/bin/env python

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020, Vanessa SOchat"
__license__ = "MPL 2.0"

import subprocess
import sys


def decodeUtf8String(inputStr):
    """Convert an UTF8 sequence into a string
    Required for compatibility with Python 2 where str==bytes
    inputStr -- Either a str or bytes instance with UTF8 encoding
    """
    return (
        inputStr
        if isinstance(inputStr, str) or not isinstance(inputStr, bytes)
        else inputStr.decode("utf8")
    )


def run_command(
    cmd,
    capture=True,
    environ=None,
    quiet=False,
):

    """run_command uses subprocess to send a command to the terminal. If
    capture is True, we use the parent stdout, so output is piped to the user.
    This means we don't return the output to parse.

    Arguments
    =========
    cmd: the command to send, should be a list for subprocess
    capture: if True, don't set stdout and have it go to console. This
             option can print a progress bar, but won't return the lines
             as output.

    Returns
    =======
    result (dict) : with return_code and lines (list of output lines)
    """
    stdout = None
    if capture:
        stdout = subprocess.PIPE

    # Use the parent stdout and stderr
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=stdout, env=environ)
    lines = []

    for line in process.communicate():
        if line:
            line = decodeUtf8String(line)
            lines.append(line)
            if not quiet:
                sys.stdout.write(line)

    output = {"lines": lines, "return_code": process.returncode}
    return output
