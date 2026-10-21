import json
from types import SimpleNamespace

import pytest

from snakedeploy.conda import CondaEnvProcessor, _parse_ensure_constraints
from snakedeploy.exceptions import UserError


@pytest.mark.parametrize(
    ("constraint", "version", "matches"),
    [
        ("python<3.12", "3.11", True),
        ("python >=3.12", "3.11", False),
        ("python=3.11", "3.11.0", True),
    ],
)
def test_parse_ensure_constraints(constraint, version, matches):
    package, version_spec = _parse_ensure_constraints([constraint])[0]

    assert package == "python"
    assert version_spec.match(version) is matches


def test_parse_invalid_ensure_constraint():
    with pytest.raises(UserError, match="Invalid --ensure constraint"):
        _parse_ensure_constraints(["python 3.12"])


@pytest.mark.parametrize(
    ("constraint", "should_pin"),
    [("python<3.12", False), ("python>=3.12", True)],
)
def test_update_pinning_only_when_ensure_constraint_violated(
    tmp_path, monkeypatch, constraint, should_pin
):
    monkeypatch.chdir(tmp_path)
    processor = CondaEnvProcessor.__new__(CondaEnvProcessor)
    processor.info = {"platform": "linux-64"}
    commands = []

    def exec_conda(command):
        commands.append(command)
        if command.startswith("list --json"):
            return SimpleNamespace(
                stdout=json.dumps([{"name": "python", "version": "3.11.0"}])
            )
        if "list --explicit" in command:
            pin_path = command.split(" > ", maxsplit=1)[1]
            (tmp_path / pin_path).write_text("@EXPLICIT\n")
        return SimpleNamespace(stdout="")

    processor.exec_conda = exec_conda
    ensure = _parse_ensure_constraints([constraint])
    warnings = []
    monkeypatch.setattr("snakedeploy.conda.logger.warning", warnings.append)

    processor.update_pinning("environment.yaml", ensure=ensure)

    pin_file = tmp_path / "environment.linux-64.pin.txt"
    assert pin_file.exists() is should_pin
    assert any("list --explicit" in command for command in commands) is should_pin
    assert bool(warnings) is should_pin
