import json

import pytest

from snakedeploy.lint import (
    BiocondaChannelOrderCheck,
    ChannelOrderCheck,
    CondaForgeChannelOrderCheck,
    lint_conda_envs,
    lint_conda_envs_cli,
)

PIN_LINE = (
    "https://conda.anaconda.org/conda-forge/linux-64/python-3.11.4-h1_0.conda#abc\n"
)


def write_env(path, channels):
    path.write_text(
        "channels:\n"
        + "".join(f"  - {c}\n" for c in channels)
        + "dependencies:\n  - python\n"
    )


def test_channel_order_check_is_abstract():
    with pytest.raises(TypeError):
        ChannelOrderCheck()


@pytest.mark.parametrize(
    ("check", "channels", "valid"),
    [
        (BiocondaChannelOrderCheck(), ["conda-forge", "bioconda", "nodefaults"], True),
        (BiocondaChannelOrderCheck(), ["bioconda", "conda-forge", "nodefaults"], False),
        (BiocondaChannelOrderCheck(), ["conda-forge", "bioconda"], False),
        (BiocondaChannelOrderCheck(), ["conda-forge", "nodefaults"], True),
        (CondaForgeChannelOrderCheck(), ["conda-forge", "nodefaults"], True),
        (CondaForgeChannelOrderCheck(), ["nodefaults", "conda-forge"], False),
        (CondaForgeChannelOrderCheck(), ["conda-forge"], False),
        (CondaForgeChannelOrderCheck(), ["bioconda", "conda-forge"], True),
        (CondaForgeChannelOrderCheck(), ["defaults"], True),
    ],
)
def test_channel_order_checks(check, channels, valid):
    assert (check.check(channels) is None) is valid


def test_lint_channels(tmp_path):
    good = tmp_path / "good.yaml"
    bad = tmp_path / "bad.yaml"
    write_env(good, ["conda-forge", "bioconda", "nodefaults"])
    write_env(bad, ["bioconda", "conda-forge"])

    result = lint_conda_envs([str(tmp_path / "*.yaml")])

    assert list(result) == [str(bad)]
    assert result[str(bad)][0]["check"] == "bioconda-channel-order"


@pytest.mark.parametrize(
    ("constraint", "violated"), [("python>=3.12", True), ("python<3.12", False)]
)
def test_lint_ensure(tmp_path, constraint, violated):
    env = tmp_path / "env.yaml"
    write_env(env, ["conda-forge", "nodefaults"])
    (tmp_path / "env.linux-64.pin.txt").write_text("@EXPLICIT\n" + PIN_LINE)

    result = lint_conda_envs([str(env)], ensure=[constraint])

    if violated:
        (violation,) = result[str(env)]
        assert violation["check"] == "ensure"
        assert violation["package"] == "python"
        assert violation["found"] == "3.11.4"
    else:
        assert result == {}


def test_lint_cli_outputs_one_json_document(tmp_path, capsys):
    ok = tmp_path / "ok.yaml"
    bad = tmp_path / "bad.yaml"
    write_env(ok, ["conda-forge", "nodefaults"])
    write_env(bad, ["nodefaults", "conda-forge"])

    code = lint_conda_envs_cli([str(ok), str(bad)])

    assert code == 1
    assert list(json.loads(capsys.readouterr().out)) == [str(bad)]
    assert lint_conda_envs_cli([str(ok)]) == 0
