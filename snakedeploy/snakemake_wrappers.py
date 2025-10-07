from pathlib import Path
import re
import tempfile
from typing import Iterable, List
from urllib.parse import urlparse
import subprocess as sp
from snakedeploy.logger import logger


def get_latest_git_tag(path: Path, repo: Path) -> str | None:
    """Get the latest git tag of any file in the given directory or below.
    Thereby ignore later git tags outside of the given directory.
    """

    # get the latest git commit that changed the given dir:
    commit = (
        sp.run(
            ["git", "rev-list", "-1", "HEAD", "--", str(path)],
            stdout=sp.PIPE,
            cwd=repo,
            check=True,
        )
        .stdout.decode()
        .strip()
    )
    # get the first git tag that includes this commit:
    # Note: We want the EARLIEST tag containing the commit, which represents
    # the first version where this wrapper reached its current state
    tags = (
        sp.run(
            ["git", "tag", "--sort", "creatordate", "--contains", commit],
            check=True,
            cwd=repo,
            stdout=sp.PIPE,
        )
        .stdout.decode()
        .strip()
        .splitlines()
    )
    if not tags:
        return None
    else:
        return tags[0]


def get_sparse_checkout_patterns() -> Iterable[str]:
    for wrapper_pattern in ("*", "*/*"):
        for filetype in ("wrapper.*", "environment.yaml"):
            yield f"/*/{wrapper_pattern}/{filetype}"
    yield "/meta/*/*/test/Snakefile"


class WrapperRepo:
    def __init__(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        logger.info("Cloning snakemake-wrappers repository...")
        sp.run(
            [
                "git",
                "clone",
                "--filter=blob:none",
                "--no-checkout",
                "https://github.com/snakemake/snakemake-wrappers.git",
                ".",
            ],
            cwd=self.tmpdir.name,
            check=True,
        )
        sp.run(
            ["git", "config", "core.sparseCheckoutCone", "false"],
            cwd=self.tmpdir.name,
            check=True,
        )
        sp.run(["git", "sparse-checkout", "disable"], cwd=self.tmpdir.name, check=True)
        sp.run(
            ["git", "sparse-checkout", "set", "--no-cone"]
            + list(get_sparse_checkout_patterns()),
            cwd=self.tmpdir.name,
            check=True,
        )
        sp.run(["git", "read-tree", "-mu", "HEAD"], cwd=self.tmpdir.name, check=True)
        self.repo_dir = Path(self.tmpdir.name)

    def get_wrapper_version(self, spec: str) -> str | None:
        if not (self.repo_dir / spec).exists():
            return None
        return get_latest_git_tag(Path(spec), self.repo_dir)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.tmpdir.cleanup()


def update_snakemake_wrappers(snakefiles: List[str]):
    """Update all snakemake wrappers to their specific latest versions."""

    with WrapperRepo() as wrapper_repo:
        for snakefile in snakefiles:
            with open(snakefile, "r") as infile:
                snakefile_content = infile.read()

            def update_spec(matchobj):
                spec = matchobj.group("spec")
                url = urlparse(spec)
                if not url.scheme:
                    parts = spec.split("/", 1)
                    if len(parts) != 2:
                        logger.warning(
                            f"Could not parse wrapper specification '{spec}' "
                            "(expected version/cat/name or version/cat/name/subcommand). "
                            "Leaving unchanged."
                        )
                        return matchobj.group()
                    old_git_ref, rest = parts
                    git_ref = wrapper_repo.get_wrapper_version(rest)
                    if git_ref is None:
                        logger.warning(
                            f"Could not determine latest version of wrapper '{rest}'. "
                            "Leaving unchanged."
                        )
                        return matchobj.group()
                    elif git_ref != old_git_ref:
                        logger.info(
                            f"Updated wrapper '{rest}' from {old_git_ref} to {git_ref}."
                        )
                    else:
                        logger.info(
                            f"Wrapper '{rest}' is already at latest version {git_ref}."
                        )
                    return (
                        matchobj.group("def")
                        + matchobj.group("quote")
                        + f"{git_ref}/{rest}"
                        + matchobj.group("quote")
                    )
                else:
                    return matchobj.group()

            logger.info(
                f"Updating snakemake-wrappers and meta-wrappers in {snakefile}..."
            )
            snakefile_content = re.sub(
                "(?P<def>(meta_)?wrapper:\\n?\\s*)(?P<quote>['\"])(?P<spec>.+)(?P=quote)",
                update_spec,
                snakefile_content,
            )
            with open(snakefile, "w") as outfile:
                outfile.write(snakefile_content)
