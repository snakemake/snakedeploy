from pathlib import Path

from snakedeploy.scaffold_plugins.common import ScaffoldPlugin


class ScaffoldSnakemakeExecutorPlugin(ScaffoldPlugin):
    def get_templates(
        self, module_path: Path, tests_path: Path
    ) -> list[tuple[str, Path]]:
        return [
            ("executor-plugins/init.py", module_path / "__init__.py"),
            ("executor-plugins/tests.py.j2", tests_path / "test_plugin.py"),
        ]

    def get_plugin_type(self) -> str:
        return "executor"

    def include_snakemake_dev_dependency(self) -> bool:
        return True
