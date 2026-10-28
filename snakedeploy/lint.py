import json
import re
from abc import ABC, abstractmethod
from glob import glob
from itertools import chain
from pathlib import Path

import yaml

from snakedeploy.conda import _parse_ensure_constraints
from snakedeploy.exceptions import UserError


class ChannelOrderCheck(ABC):
    """Generic check of the channel order of a conda env definition."""

    name = "channel-order"

    @abstractmethod
    def expected_channels(self, channels: list) -> list | None:
        """Return the expected channel order for the given channels,
        or None if this check is not applicable."""

    def check(self, channels: list) -> dict | None:
        expected = self.expected_channels(channels)
        if expected is None or list(channels) == expected:
            return None
        return {
            "check": self.name,
            "message": f"Channels should be {expected}, found {list(channels)}.",
            "expected": expected,
            "found": list(channels),
        }


class BiocondaChannelOrderCheck(ChannelOrderCheck):
    name = "bioconda-channel-order"

    def expected_channels(self, channels):
        if "bioconda" in channels:
            return ["conda-forge", "bioconda", "nodefaults"]
        return None


class CondaForgeChannelOrderCheck(ChannelOrderCheck):
    name = "conda-forge-channel-order"

    def expected_channels(self, channels):
        if "conda-forge" in channels and "bioconda" not in channels:
            return ["conda-forge", "nodefaults"]
        return None


CHANNEL_ORDER_CHECKS = [BiocondaChannelOrderCheck(), CondaForgeChannelOrderCheck()]


def _pinned_versions(pin_file: Path) -> dict:
    versions = {}
    for line in pin_file.read_text().splitlines():
        line = line.strip()
        if not line.startswith(("http://", "https://", "file:")):
            continue
        filename = re.sub(
            r"(\.conda|\.tar\.bz2)$", "", line.split("#")[0].rsplit("/", 1)[-1]
        )
        parts = filename.rsplit("-", 2)
        if len(parts) == 3:
            versions[parts[0].lower()] = parts[1]
    return versions


def _check_ensure(env_path: str, ensure: list) -> list:
    pin_files = sorted(Path(env_path).parent.glob(f"{Path(env_path).stem}.*.pin.txt"))
    violations = []
    for pin_file in pin_files:
        versions = _pinned_versions(pin_file)
        for package, spec in ensure:
            if package in versions and not spec.match(versions[package]):
                violations.append(
                    {
                        "check": "ensure",
                        "pin_file": str(pin_file),
                        "package": package,
                        "constraint": str(spec),
                        "found": versions[package],
                        "message": f"{package}=={versions[package]} in {pin_file} "
                        f"violates {spec}.",
                    }
                )
    return violations


def lint_conda_envs(conda_env_paths: list, ensure=None) -> dict:
    """Lint the given conda envs, return the violations per env."""
    parsed_ensure = _parse_ensure_constraints(ensure)
    env_paths = sorted(set(chain.from_iterable(map(glob, conda_env_paths))))
    result = {}
    for env_path in env_paths:
        with open(env_path) as f:
            try:
                env = yaml.safe_load(f) or {}
            except yaml.YAMLError as e:
                raise UserError(f"Cannot parse {env_path}: {e}") from e
        violations = []
        channels = env.get("channels") or []
        for check in CHANNEL_ORDER_CHECKS:
            violation = check.check(channels)
            if violation:
                violations.append(violation)
        violations.extend(_check_ensure(env_path, parsed_ensure))
        if violations:
            result[env_path] = violations
    return result


def lint_conda_envs_cli(conda_env_paths: list, ensure=None) -> int:
    violations = lint_conda_envs(conda_env_paths, ensure=ensure)
    print(json.dumps(violations, indent=2))
    return 1 if violations else 0
