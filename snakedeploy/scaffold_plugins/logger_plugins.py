from pathlib import Path

from snakedeploy.scaffold_plugins.common import ScaffoldPlugin


class ScaffoldSnakemakeLoggerPlugin(ScaffoldPlugin):
    name = "scaffold-snakemake-logger-plugin"
    description = (
        "Scaffolds a snakemake logger plugin by adding recommended "
        "dependencies and code snippets."
    )

    def get_templates(
        self, module_path: Path, tests_path: Path
    ) -> list[tuple[str, Path]]:
        return [
            ("logger-plugins/init.py", module_path / "__init__.py"),
            ("logger-plugins/tests.py", tests_path / "test_plugin.py"),
        ]

    def get_plugin_type(self) -> str:
        return "logger"

    def include_snakemake_dev_dependency(self) -> bool:
        return False
