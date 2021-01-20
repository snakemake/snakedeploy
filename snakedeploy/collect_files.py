import sys
from glob import glob
import re
from collections import namedtuple

from snakedeploy.exceptions import UserError
from snakedeploy.utils import read_csv


def collect_files(config_sheet_path: str):
    """Given a configuration sheet path with input patterns, print matches
    of samples to STDOUT
    """
    config_sheet = read_csv(config_sheet_path, sep="\t")

    # Input patterns are in the first column, add regex to last column
    for row in config_sheet:
        row.append(re.compile(row[0]))

    for item in sys.stdin:
        item = item[:-1]  # remove newline

        matches = list(
            filter(
                lambda match: match.match is not None, get_matches(item, config_sheet)
            )
        )

        if not matches:
            raise UserError(f"No input pattern in config sheet matches {item}.")
        elif len(matches) > 1:
            raise UserError(f"Item {item} matches multiple input patterns.")

        match = matches[0]
        pattern = match.rule.glob_pattern.format(
            **{
                key: autoconvert(value)
                for key, value in match.match.groupdict().items()
            }
        )
        files = sorted(glob(pattern))
        if not files:
            raise UserError(f"No files were found for {item} with pattern {pattern}.")

        print(item, *files, sep="\t")


Match = namedtuple("Match", "rule match")


def get_matches(item, config_sheet: list):
    return (Match(rule, rule[-1].match(item)) for rule in config_sheet)


def autoconvert(value):
    try:
        return int(value)
    except ValueError:
        return value
