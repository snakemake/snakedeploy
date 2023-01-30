from collections import namedtuple
import copy
import json
import os
from pathlib import Path
import subprocess as sp
import tempfile
import re
from glob import glob
from itertools import chain
from urllib3.util.retry import Retry
import random

from packaging import version as packaging_version
import yaml
from github import Github, GithubException
from reretry import retry

from snakedeploy.exceptions import UserError
from snakedeploy.logger import logger
from snakedeploy.utils import YamlDumper


def pin_conda_envs(conda_env_paths: list, conda_frontend="mamba"):
    """Pin given conda envs by creating <conda-env>.<platform>.pin.txt
    files with explicit URLs for all packages in each env."""
    return CondaEnvProcessor(conda_frontend=conda_frontend).process(
        conda_env_paths, create_prs=False, update_envs=False, pin_envs=True
    )


def update_conda_envs(
    conda_env_paths: list,
    conda_frontend="mamba",
    create_prs=False,
    pin_envs=False,
    pr_add_label=False,
    entity_regex=None,
    warn_on_error=False,
):
    """Update the given conda env definitions such that all dependencies
    in them are set to the latest feasible versions."""
    return CondaEnvProcessor(conda_frontend=conda_frontend).process(
        conda_env_paths,
        create_prs=create_prs,
        update_envs=True,
        pin_envs=pin_envs,
        pr_add_label=pr_add_label,
        entity_regex=entity_regex,
        warn_on_error=warn_on_error,
    )


File = namedtuple("File", "path, content, is_updated, msg")


class CondaEnvProcessor:
    def __init__(self, conda_frontend="mamba"):
        self.conda_frontend = conda_frontend
        self.info = json.loads(
            sp.check_output(
                f"{conda_frontend} info --json",
                universal_newlines=True,
                shell=True,
                stderr=sp.PIPE,
            )
        )

    def process(
        self,
        conda_env_paths,
        create_prs=False,
        update_envs=True,
        pin_envs=True,
        pr_add_label=False,
        entity_regex=None,
        warn_on_error=False,
    ):
        repo = None
        if create_prs:
            g = Github(
                os.environ["GITHUB_TOKEN"],
                retry=Retry(
                    total=10, status_forcelist=(500, 502, 504), backoff_factor=0.3
                ),
            )
            repo = g.get_repo(os.environ["GITHUB_REPOSITORY"]) if create_prs else None
        conda_envs = list(chain.from_iterable(map(glob, conda_env_paths)))
        random.shuffle(conda_envs)

        if not conda_envs:
            logger.info(
                f"No conda envs found at given paths: {', '.join(conda_env_paths)}"
            )
        for conda_env_path in conda_envs:
            if create_prs:
                if not update_envs:
                    raise UserError(
                        "Creating PRs for only pinning updates is not supported."
                    )
                entity = conda_env_path
                if entity_regex is not None:
                    m = re.match(entity_regex, conda_env_path)
                    if m is None:
                        raise UserError(
                            f"Given --entity-regex did not match any {conda_env_path}."
                        )
                    try:
                        entity = m.group("entity")
                    except IndexError:
                        raise UserError(
                            "No group 'entity' found in given --entity-regex."
                        )
                if pr_add_label and not entity_regex:
                    raise UserError(
                        "Cannot add label to PR without --entity-regex specified."
                    )
                pr = PR(
                    f"perf: autobump {entity}",
                    f"Automatic update of {entity}.",
                    f"autobump/{entity.replace('/', '-')}",
                    repo,
                    label=entity if pr_add_label else None,
                )
            else:
                pr = None
            try:
                updated = False
                if update_envs:
                    logger.info(f"Updating {conda_env_path}...")
                    updated = self.update_env(
                        conda_env_path, pr=pr, warn_on_error=warn_on_error
                    )
                if pin_envs and (not update_envs or updated):
                    logger.info(f"Pinning {conda_env_path}...")
                    self.update_pinning(conda_env_path, pr)
            except sp.CalledProcessError as e:
                msg = f"Failed for conda env {conda_env_path}:\n{e.stderr}\n{e.stdout}"
                if warn_on_error:
                    logger.warning(msg)
                else:
                    raise UserError(msg)
            if create_prs:
                pr.create()

    def update_env(
        self,
        conda_env_path,
        pr=None,
        warn_on_error=False,
    ):
        spec_re = re.compile("(?P<name>[^=>< ]+)[ =><]+")
        with open(conda_env_path, "r") as infile:
            conda_env = yaml.load(infile, Loader=yaml.SafeLoader)

        def process_dependencies(func):
            def process_dependency(dep):
                if isinstance(dep, dict):
                    # leave e.g. pip subdicts unchanged
                    return dep
                m = spec_re.match(dep)
                if m is None:
                    # cannot parse the spec, leave unchanged
                    return dep
                return func(m.group("name"))

            return [process_dependency(dep) for dep in conda_env["dependencies"]]

        def get_pkg_versions(conda_env_path):
            with tempfile.TemporaryDirectory(dir=".", prefix=".") as tmpdir:
                self.exec_conda(f"env create --file {conda_env_path} --prefix {tmpdir}")
                pkg_versions = {
                    pkg["name"]: pkg["version"]
                    for pkg in json.loads(
                        self.exec_conda(f"list --json --prefix {tmpdir}").stdout
                    )
                }
                self.exec_conda(f"env remove --prefix {tmpdir}")
            return pkg_versions

        logger.info("Resolving prior versions...")
        prior_pkg_versions = get_pkg_versions(conda_env_path)

        unconstrained_deps = process_dependencies(lambda name: name)
        unconstrained_env = dict(conda_env)
        unconstrained_env["dependencies"] = unconstrained_deps

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", dir=".", prefix="."
        ) as tmpenv:
            yaml.dump(unconstrained_env, tmpenv, Dumper=YamlDumper)
            logger.info("Resolving posterior versions...")
            posterior_pkg_versions = get_pkg_versions(tmpenv.name)

        def downgraded():
            for pkg_name, version in posterior_pkg_versions.items():
                try:
                    version = packaging_version.parse(version)
                except packaging_version.InvalidVersion as e:
                    raise UserError(
                        f"Cannot parse version {version} of package {pkg_name}: {e}"
                    )
                prior_version = prior_pkg_versions.get(pkg_name)
                if prior_version is not None and version < packaging_version.parse(
                    prior_version
                ):
                    yield pkg_name

        downgraded = list(downgraded())
        if downgraded:
            msg = (
                f"Env {conda_env_path} could not be updated because the following packages "
                f"would be downgraded: {', '.join(downgraded)}. Please consider a manual update "
                "of the environment."
            )
            if warn_on_error:
                logger.warning(msg)
            else:
                raise UserError(msg)

        orig_env = copy.deepcopy(conda_env)

        conda_env["dependencies"] = process_dependencies(
            lambda name: f"{name} ={posterior_pkg_versions[name]}"
        )
        if orig_env != conda_env:
            with open(conda_env_path, "w") as outfile:
                yaml.dump(conda_env, outfile, Dumper=YamlDumper)
            if pr:
                with open(conda_env_path, "r") as infile:
                    content = infile.read()

                pr.add_file(
                    conda_env_path,
                    content,
                    is_updated=True,
                    msg=f"perf: update {conda_env_path}.",
                )
            return True
        else:
            logger.info("No updates in env.")
            return False

    def update_pinning(self, conda_env_path, pr=None):
        pin_file = Path(conda_env_path).with_suffix(f".{self.info['platform']}.pin.txt")
        old_content = None
        updated = False
        if pin_file.exists():
            with open(pin_file, "r") as infile:
                old_content = infile.read()

        with tempfile.TemporaryDirectory(dir=".", prefix=".") as tmpdir:
            self.exec_conda(f"env create --prefix {tmpdir} --file {conda_env_path}")
            self.exec_conda(
                f"list --explicit --md5 --prefix {tmpdir} > {tmpdir}/pin.txt"
            )
            with open(f"{tmpdir}/pin.txt", "r") as infile:
                new_content = infile.read()
            updated = old_content != new_content
            if updated:
                with open(pin_file, "w") as outfile:
                    outfile.write(new_content)
                if pr:
                    msg = (
                        "perf: update env pinning."
                        if old_content is not None
                        else f"feat: add pinning for {conda_env_path}."
                    )
                    pr.add_file(
                        pin_file,
                        new_content,
                        is_updated=old_content is not None,
                        msg=msg,
                    )
            self.exec_conda(f"env remove --prefix {tmpdir}")

    def exec_conda(self, subcmd):
        return sp.run(
            f"{self.conda_frontend} {subcmd}",
            shell=True,
            stderr=sp.PIPE,
            stdout=sp.PIPE,
            universal_newlines=True,
            check=True,
        )


class PR:
    def __init__(self, title, body, branch, repo, label=None):
        self.title = title
        self.body = body
        self.files = []
        self.branch = branch
        self.repo = repo
        self.base_ref = (
            os.environ.get("GITHUB_BASE_REF") or os.environ["GITHUB_REF_NAME"]
        )
        self.label = label

    def add_file(self, filepath, content, is_updated, msg):
        self.files.append(File(filepath, content, is_updated, msg))

    @retry(tries=2, delay=60)
    def create(self):
        import pdb

        pdb.set_trace()
        if not self.files:
            logger.info("No files to commit.")
            return

        branch_exists = False
        try:
            b = self.repo.get_branch(self.branch)
            logger.info(f"Branch {b} already exists.")
            branch_exists = True
        except GithubException as e:
            if e.status != 404:
                raise e
            logger.info(f"Creating branch {self.branch}...")
            self.repo.create_git_ref(
                ref=f"refs/heads/{self.branch}",
                sha=self.repo.get_branch(self.base_ref).commit.sha,
            )
        for file in self.files:
            if file.is_updated:
                sha = None
                if branch_exists:
                    logger.info(
                        f"Obtaining sha of {file.path} on branch {self.branch}..."
                    )
                    sha = self.repo.get_contents(file.path, self.branch).sha
                else:
                    logger.info(
                        f"Obtaining sha of {file.path} on branch {self.base_ref}..."
                    )
                    sha = self.repo.get_contents(file.path, self.base_ref).sha
                self.repo.update_file(
                    file.path,
                    file.msg,
                    file.content,
                    sha,
                    branch=self.branch,
                )
            else:
                self.repo.create_file(
                    file.path, file.msg, file.content, branch=self.branch
                )
        pr_exists = any(
            pr.head.label.split(":", 1)[1] == self.branch
            for pr in self.repo.get_pulls(state="open", base=self.base_ref)
        )
        if pr_exists:
            logger.info("PR already exists.")
        else:
            pr = self.repo.create_pull(
                title=self.title,
                body=self.body,
                head=self.branch,
                base=self.base_ref,
            )
            pr.add_to_labels(self.label)
            logger.info(f"Created PR: {pr.html_url}")
