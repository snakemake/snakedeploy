import json
from pathlib import Path
import subprocess as sp
import tempfile
import re
from abc import ABC, abstractmethod


import yaml

from snakedeploy.exceptions import UserError
from snakedeploy.logger import logger


def pin_conda_envs(conda_env_paths: list, conda_frontend="mamba"):
    """Pin given conda envs by creating <conda-env>.<platform>.pin.txt
    files with explicit URLs for all packages in each env."""
    return PinCondaEnvProcessor(conda_frontend=conda_frontend).process(conda_env_paths)


def update_conda_envs(conda_env_paths: list, conda_frontend="mamba"):
    """Update the given conda env definitions such that all dependencies
    in them are set to the latest feasible versions."""
    return UpdateCondaEnvProcessor(conda_frontend=conda_frontend).process(
        conda_env_paths
    )


class CondaEnvProcessor(ABC):
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

    def process(self, conda_env_paths):
        for conda_env_path in conda_env_paths:
            logger.info(f"{self.get_process_msg()} {conda_env_path}...")
            try:
                self.process_env(conda_env_path)
            except sp.CalledProcessError as e:
                raise UserError(
                    f"Failed for conda env {conda_env_path}:" "\n" f"{e.stderr}"
                )

    @abstractmethod
    def process_env(self, conda_env_path):
        ...

    def exec_conda(self, subcmd):
        return sp.check_output(
            f"{self.conda_frontend} {subcmd}",
            shell=True,
            stderr=sp.PIPE,
            universal_newlines=True,
        )


class UpdateCondaEnvProcessor(CondaEnvProcessor):
    def get_process_msg(self):
        return "Updating"

    def process_env(self, conda_env_path):
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
            yaml.dump(unconstrained_env, tmpenv)
            self.exec_conda(f"env create --file {tmpenv.name} --prefix {tmpdir}")
            pkg_versions = {
                pkg["name"]: pkg["version"]
                for pkg in json.loads(self.exec_conda(f"list --json --prefix {tmpdir}"))
            }
            self.exec_conda(f"env remove --prefix {tmpdir}")

        conda_env["dependencies"] = process_dependencies(
            lambda name: f"{name} ={pkg_versions[name]}"
        )
        with open(conda_env_path, "w") as outfile:
            yaml.dump(conda_env, outfile)


class PinCondaEnvProcessor(CondaEnvProcessor):
    def get_process_msg(self):
        return "Pinning"

    def process_env(self, conda_env_path):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.exec_conda(f"env create --prefix {tmpdir} --file {conda_env_path}")
            pin_file = Path(conda_env_path).with_suffix(
                f".{self.info['platform']}.pin.txt"
            )
            self.exec_conda(f"list --explicit --md5 --prefix {tmpdir} > {pin_file}")
            self.exec_conda(f"env remove --prefix {tmpdir}")
