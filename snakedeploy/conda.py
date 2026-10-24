import copy
import json
import random
import re
import subprocess as sp
import tempfile
from glob import glob
from itertools import chain
from pathlib import Path

import yaml
from packaging import version as packaging_version

from snakedeploy.conda_version import VersionOrder, VersionSpec
from snakedeploy.exceptions import (
    InvalidVersionSpec,
    UnsatisfiedCondaConstraintsError,
    UserError,
)
from snakedeploy.logger import logger
from snakedeploy.prs import PR, get_repo
from snakedeploy.utils import YamlDumper


def _parse_ensure_constraints(constraints):
    parsed_constraints = []
    spec_re = re.compile(r"^\s*([A-Za-z0-9_.-]+)\s*(==|!=|~=|<=|>=|=|<|>)\s*(\S+)\s*$")
    for constraint in constraints or ():
        match = spec_re.match(constraint)
        if match is None:
            raise UserError(
                f"Invalid --ensure constraint '{constraint}'; expected a package name "
                "and version specifier, e.g. 'python<3.12'."
            )
        package, operator, version = match.groups()
        version_spec = operator + version
        try:
            parsed_constraints.append((package.lower(), VersionSpec(version_spec)))
        except InvalidVersionSpec as e:
            raise UserError(f"Invalid --ensure constraint '{constraint}': {e}") from e
    return parsed_constraints


def pin_conda_envs(
    conda_env_paths: list,
    conda_frontend="mamba",
    create_prs=False,
    pr_add_label=False,
    entity_regex=None,
    warn_on_error=False,
    ensure=None,
    only_if_ensure_is_unsatisfied=False,
):
    """Pin given conda envs by creating <conda-env>.<platform>.pin.txt
    files with explicit URLs for all packages in each env."""
    return CondaEnvProcessor(conda_frontend=conda_frontend).process(
        conda_env_paths,
        update_envs=False,
        pin_envs=True,
        create_prs=create_prs,
        pr_add_label=pr_add_label,
        entity_regex=entity_regex,
        warn_on_error=warn_on_error,
        ensure=_parse_ensure_constraints(ensure),
        only_if_ensure_is_unsatisfied=only_if_ensure_is_unsatisfied,
    )


def update_conda_envs(
    conda_env_paths: list,
    conda_frontend="mamba",
    create_prs=False,
    pin_envs=False,
    pr_add_label=False,
    entity_regex=None,
    warn_on_error=False,
    ensure=None,
    only_if_ensure_is_unsatisfied=False,
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
        ensure=_parse_ensure_constraints(ensure),
        only_if_ensure_is_unsatisfied=only_if_ensure_is_unsatisfied,
    )


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
        create_prs: bool = False,
        update_envs: bool = True,
        pin_envs: bool = True,
        pr_add_label: bool = False,
        entity_regex: str | None = None,
        warn_on_error: bool = False,
        ensure=None,
        only_if_ensure_is_unsatisfied: bool = False,
    ):
        repo = None
        if create_prs:
            repo = get_repo()
        conda_envs = list(chain.from_iterable(map(glob, conda_env_paths)))
        random.shuffle(conda_envs)

        if not conda_envs:
            logger.info(
                f"No conda envs found at given paths: {', '.join(conda_env_paths)}"
            )
        errors = []
        for conda_env_path in conda_envs:
            if create_prs:
                if pr_add_label and not entity_regex:
                    raise UserError(
                        "Cannot add label to PR without --entity-regex specified."
                    )

                assert pin_envs or update_envs, (
                    "bug: either pin_envs or update_envs must be True"
                )
                mode = "bump" if update_envs else "pin"
                pr = PR(
                    f"perf: auto{mode} {conda_env_path}",
                    f"Automatic {mode} of {conda_env_path}.",
                    f"auto{mode}/{conda_env_path.replace('/', '-')}",
                    repo,
                    entity=conda_env_path,
                    label_entity_regex=entity_regex if pr_add_label else None,
                )
            else:
                pr = None
            try:
                updated = False
                if update_envs:
                    updated = self.update_env(
                        conda_env_path,
                        pr=pr,
                        ensure=ensure,
                        only_if_ensure_is_unsatisfied=only_if_ensure_is_unsatisfied,
                    )
                if pin_envs and (
                    not update_envs
                    or updated
                    or not self.get_pin_file_path(conda_env_path).exists()
                ):
                    self.update_pinning(
                        conda_env_path,
                        pr,
                        ensure=ensure if not update_envs else None,
                        only_if_ensure_is_unsatisfied=only_if_ensure_is_unsatisfied
                        if not update_envs
                        else False,
                    )
            except sp.CalledProcessError as e:
                msg = f"Failed for conda env {conda_env_path}:\n{e.stderr}\n{e.stdout}"
                errors.append(UserError(msg))
            except UserError as e:
                errors.append(e)
            if create_prs:
                assert pr is not None
                pr.create()

        if errors:
            user_error = UserError(suberrors=errors)
            if warn_on_error:
                logger.warning(str(user_error))
            else:
                raise user_error

    def update_env(
        self,
        conda_env_path,
        pr=None,
        ensure=None,
        only_if_ensure_is_unsatisfied: bool = False,
    ):
        logger.info(f"Checking {conda_env_path} for updates...")
        spec_re = re.compile("(?P<name>[^=>< ]+)[ =><]+")
        with open(conda_env_path, "r") as infile:
            conda_env = yaml.load(infile, Loader=yaml.SafeLoader)

        def process_dependencies(func, only_constrained=False):
            def process_dependency(dep):
                if isinstance(dep, dict):
                    # leave e.g. pip subdicts unchanged
                    return dep
                m = spec_re.match(dep.strip())
                if m is None:
                    if only_constrained:
                        return None
                    else:
                        # cannot parse the spec, leave unchanged
                        return dep
                return func(m.group("name"))

            return list(
                filter(
                    lambda item: item is not None,
                    map(process_dependency, conda_env["dependencies"]),
                )
            )

        def get_pkg_versions(conda_env_path, ensure=None):
            with tempfile.TemporaryDirectory(dir=".", prefix=".") as tmpdir:
                self.exec_conda(f"env create --file {conda_env_path} --prefix {tmpdir}")
                package_info = self.get_package_info(tmpdir)
                pkg_versions = self.get_package_versions(package_info)
                unsatisfied_constraints = self.get_unsatified_constraints(
                    package_versions=pkg_versions, ensure=ensure
                )
                self.exec_conda(f"env remove --prefix {tmpdir} -y")
            return pkg_versions, package_info, unsatisfied_constraints

        logger.info("Resolving prior versions...")
        prior_pkg_versions, _, prior_unsatisfied_constraints = get_pkg_versions(
            conda_env_path, ensure=ensure
        )
        if only_if_ensure_is_unsatisfied and not prior_unsatisfied_constraints:
            return

        unconstrained_deps = process_dependencies(lambda name: name)
        unconstrained_env = dict(conda_env)
        unconstrained_env["dependencies"] = unconstrained_deps

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", dir=".", prefix="."
        ) as tmpenv:
            yaml.dump(unconstrained_env, tmpenv, Dumper=YamlDumper)
            logger.info("Resolving posterior versions...")
            (
                posterior_pkg_versions,
                posterior_pkg_json,
                posterior_unsatisfied_constraints,
            ) = get_pkg_versions(tmpenv.name, ensure=ensure)

        if posterior_unsatisfied_constraints:
            raise UnsatisfiedCondaConstraintsError(
                posterior_unsatisfied_constraints, conda_env_path
            )

        def downgraded():
            for pkg_name, version in posterior_pkg_versions.items():
                try:
                    version = VersionOrder(version)
                except packaging_version.InvalidVersion as e:
                    logger.debug(json.dumps(posterior_pkg_json, indent=2))
                    raise UserError(
                        f"Cannot parse version {version} of package {pkg_name}: {e}"
                    )
                prior_version = prior_pkg_versions.get(pkg_name)
                if prior_version is not None and version < VersionOrder(prior_version):
                    yield pkg_name

        downgraded = set(
            process_dependencies(lambda name: name, only_constrained=True)
        ) & set(downgraded())
        if downgraded:
            msg = (
                f"Env {conda_env_path} could not be updated because the following packages "
                f"would be downgraded: {', '.join(downgraded)}. Please consider a manual update "
                "of the environment."
            )
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
            logger.info(f"Updated {conda_env_path}.")
            return True
        else:
            logger.info(f"No updates in {conda_env_path}.")
            return False

    def get_pin_file_path(self, conda_env_path):
        return Path(conda_env_path).with_suffix(f".{self.info['platform']}.pin.txt")

    def get_package_info(self, prefix):
        return json.loads(self.exec_conda(f"list --json --prefix {prefix}").stdout)

    def get_package_versions(self, package_info):
        return {package["name"].lower(): package["version"] for package in package_info}

    def get_unsatified_constraints(self, package_versions, ensure=None):
        unsatisfied_constraints = []
        if ensure:
            unsatisfied_constraints = [
                (package, version_spec)
                for package, version_spec in ensure
                if package in package_versions
                and not version_spec.match(package_versions[package])
            ]

        return unsatisfied_constraints

    def pinning_ensure_is_satisfied(self, conda_env_path, ensure):
        pin_file = self.get_pin_file_path(conda_env_path)
        if not pin_file.exists():
            return False
        if ensure:
            with tempfile.TemporaryDirectory(dir=".", prefix=".") as tmpdir:
                self.exec_conda(f"create --prefix {tmpdir} --file {pin_file}")
                unsatisfied_constraints = self.get_unsatified_constraints(
                    package_versions=self.get_package_versions(
                        self.get_package_info(tmpdir)
                    ),
                    ensure=ensure,
                )
                self.exec_conda(f"env remove --prefix {tmpdir} -y")
                if unsatisfied_constraints:
                    return False
        return True

    def update_pinning(
        self, conda_env_path, pr=None, ensure=None, only_if_ensure_is_unsatisfied=False
    ):
        logger.info(f"Checking {conda_env_path} pinning...")
        pin_file = self.get_pin_file_path(conda_env_path)
        old_content = None
        updated = False
        if only_if_ensure_is_unsatisfied and self.pinning_ensure_is_satisfied(
            conda_env_path, ensure
        ):
            logger.info(f"Pinning for {conda_env_path} already satisfies --ensure.")
            return False

        if pin_file.exists():
            with open(pin_file, "r") as infile:
                old_content = infile.read()

        with tempfile.TemporaryDirectory(dir=".", prefix=".") as tmpdir:
            self.exec_conda(f"env create --prefix {tmpdir} --file {conda_env_path}")
            unsatisfied_constraints = self.get_unsatified_constraints(
                package_versions=self.get_package_versions(
                    self.get_package_info(tmpdir)
                ),
                ensure=ensure,
            )
            self.exec_conda(
                f"list --explicit --md5 --prefix {tmpdir} > {tmpdir}/pin.txt"
            )
            with open(f"{tmpdir}/pin.txt", "r") as infile:
                new_content = infile.read()
            updated = old_content != new_content

            if unsatisfied_constraints:
                logger.warning(
                    f"Unsatisfied constraints for {conda_env_path} (full error upon termination)."
                )
                raise UnsatisfiedCondaConstraintsError(
                    unsatisfied_constraints, conda_env_path
                )

            if updated:
                logger.info(f"Updated pinning for {conda_env_path}.")
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
            else:
                logger.info(f"No updates for pinning of {conda_env_path}.")
            self.exec_conda(f"env remove --prefix {tmpdir} -y")

    def exec_conda(self, subcmd):
        return sp.run(
            f"{self.conda_frontend} {subcmd}",
            shell=True,
            capture_output=True,
            text=True,
            check=True,
        )
