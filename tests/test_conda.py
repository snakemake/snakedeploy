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
    ("constraint", "should_raise"),
    [("python<3.12", False), ("python>=3.12", True)],
)
def test_update_pinning_always_updates_and_checks_ensure(
    tmp_path, monkeypatch, constraint, should_raise
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

    if should_raise:
        with pytest.raises(UserError, match="Could not satisfy --ensure constraints"):
            processor.update_pinning("environment.yaml", ensure=ensure)
    else:
        processor.update_pinning("environment.yaml", ensure=ensure)

    pin_file = tmp_path / "environment.linux-64.pin.txt"
    assert pin_file.exists() is not should_raise
    assert any("list --explicit" in command for command in commands)
