from collections import namedtuple
import copy
import json
import os
from pathlib import Path
import subprocess as sp
import tempfile
import re


import yaml
from github import Github, GithubException

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
    conda_env_paths: list, conda_frontend="mamba", create_prs=False, pin_envs=False
):
    """Update the given conda env definitions such that all dependencies
    in them are set to the latest feasible versions."""
    return CondaEnvProcessor(conda_frontend=conda_frontend).process(
        conda_env_paths, create_prs=create_prs, update_envs=True, pin_envs=pin_envs
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
        self, conda_env_paths, create_prs=False, update_envs=True, pin_envs=True
    ):
        repo = None
        if create_prs:
            g = Github(os.environ["GITHUB_TOKEN"])
            repo = (
                g.get_repo(os.environ["GITHUB_ACTION_REPOSITORY"])
                if create_prs
                else None
            )
        for conda_env_path in conda_env_paths:
            if create_prs:
                if not update_envs:
                    raise UserError(
                        "Creating PRs for only pinning updates is not supported."
                    )
                pr = PR(
                    f"perf: autobump {conda_env_path}",
                    f"Automatic update of {conda_env_path}.",
                    f"autobump/{conda_env_path}",
                    repo,
                )
            else:
                pr = None
            try:
                if update_envs:
                    logger.info(f"Updating {conda_env_path}...")
                    self.update_env(conda_env_path, pr)
                if pin_envs:
                    logger.info(f"Pinning {conda_env_path}...")
                    self.update_pinning(conda_env_path, pr)
            except sp.CalledProcessError as e:
                raise UserError(
                    f"Failed for conda env {conda_env_path}:" "\n" f"{e.stderr}"
                )
            if create_prs:
                pr.create()

    def update_env(
        self,
        conda_env_path,
        pr=None,
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

        unconstrained_deps = process_dependencies(lambda name: name)
        unconstrained_env = dict(conda_env)
        unconstrained_env["dependencies"] = unconstrained_deps
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml"
        ) as tmpenv, tempfile.TemporaryDirectory() as tmpdir:
            yaml.dump(unconstrained_env, tmpenv, Dumper=YamlDumper)
            self.exec_conda(f"env create --file {tmpenv.name} --prefix {tmpdir}")
            pkg_versions = {
                pkg["name"]: pkg["version"]
                for pkg in json.loads(self.exec_conda(f"list --json --prefix {tmpdir}"))
            }
            self.exec_conda(f"env remove --prefix {tmpdir}")

        orig_env = copy.deepcopy(conda_env)

        conda_env["dependencies"] = process_dependencies(
            lambda name: f"{name} ={pkg_versions[name]}"
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
        else:
            logger.info("No updates in env.")

    def update_pinning(self, conda_env_path, pr=None):
        pin_file = Path(conda_env_path).with_suffix(f".{self.info['platform']}.pin.txt")
        old_content = None
        updated = False
        if pin_file.exists():
            with open(pin_file, "r") as infile:
                old_content = infile.read()

        with tempfile.TemporaryDirectory() as tmpdir:
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
        return sp.check_output(
            f"{self.conda_frontend} {subcmd}",
            shell=True,
            stderr=sp.PIPE,
            universal_newlines=True,
        )


class PR:
    def __init__(self, title, body, branch, repo):
        self.title = title
        self.body = body
        self.files = []
        self.branch = branch
        self.repo = repo

    def add_file(self, filepath, content, is_updated, msg):
        self.files.append(File(filepath, content, is_updated, msg))

    def create(self):
        if not self.files:
            logger.info("No files to commit.")
        branch_exists = False
        try:
            self.repo.get_branch(self.branch)
            branch_exists = True
        except GithubException as e:
            if e.status != 404:
                raise e
            self.repo.create_git_ref(
                ref=f"refs/heads/{self.branch}",
                sha=self.repo.get_branch("master").commit.sha,
            )
        for file in self.files:
            if file.is_updated:
                if branch_exists:
                    sha = self.repo.get_contents(file.path, self.branch).sha
                else:
                    sha = self.repo.get_contents(file.path).sha
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
            pr.head.label == self.branch
            for pr in self.repo.get_pulls(state="open", base="master")
        )
        if pr_exists:
            logger.info("PR already exists.")
        else:
            pr = self.repo.create_pull(
                title=self.title,
                body=self.body,
                head=self.branch,
                base="master",
            )
            logger.info(f"Created PR: {pr.html_url}")
