import sys
from glob import glob
import re

from snakedeploy.exceptions import UserError

def collect_files(input_pattern: str, glob_pattern: str):
    input_regex = re.compile(input_pattern)
    for item in sys.stdin:
        item = item[:-1] # remove newline
        match = input_regex.match(item)
        if match is None:
            raise UserError(f"input pattern {input_pattern} does not match {item}")
        files = sorted(glob(glob_pattern.format(**{key: autoconvert(value) for key, value in match.groupdict().items()})))
        print(item, *files, sep="\t")
    

def autoconvert(value):
    try:
        return int(value)
    except ValueError:
        return value