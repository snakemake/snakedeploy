import sys
from glob import glob

from snakedeploy.exceptions import UserError

def collect_files(input_pattern: str, glob_pattern: str):
    input_regex = re.compile(input_pattern)
    for item in sys.stdin:
        match = input_regex.match(item)
        if match is None:
            raise UserError(f"input pattern {input_pattern} does not match {item}")
        files = list(glob(glob_pattern.format(**match.groupdict())))
        print(item, *files, sep="\t")