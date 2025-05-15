import re
from typing import List
from urllib.parse import urlparse
from snakedeploy.logger import logger

from github import Github


def update_snakemake_wrappers(snakefiles: List[str], git_ref: str):
    """Set all snakemake wrappers to the given git ref (e.g. tag or branch)."""

    if git_ref is None:
        logger.info("Obtaining latest release of snakemake-wrappers...")
        github = Github()
        repo = github.get_repo("snakemake/snakemake-wrappers")
        releases = repo.get_releases()
        git_ref = releases[0].tag_name

    for snakefile in snakefiles:
        with open(snakefile, "r") as infile:
            snakefile_content = infile.read()

        def update_spec(matchobj):
            spec = matchobj.group("spec")
            url = urlparse(spec)
            if not url.scheme:
                old_git_ref, rest = spec.split("/", 1)
                return (
                    matchobj.group("def")
                    + matchobj.group("quote")
                    + f"{git_ref}/{rest}"
                    + matchobj.group("quote")
                )
            else:
                return matchobj.group()

        logger.info(f"Updating snakemake-wrappers in {snakefile} to {git_ref}...")
        snakefile_content = re.sub(
            "(?P<def>wrapper:\\n?\\s*)(?P<quote>['\"])(?P<spec>.+)(?P=quote)",
            update_spec,
            snakefile_content,
        )
        with open(snakefile, "w") as outfile:
            outfile.write(snakefile_content)
