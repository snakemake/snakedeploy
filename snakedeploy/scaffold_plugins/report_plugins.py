from pathlib import Path

from snakedeploy.scaffold_plugins.common import ScaffoldPlugin


class ScaffoldSnakemakeReportPlugin(ScaffoldPlugin):
    def get_templates(
        self, module_path: Path, tests_path: Path
    ) -> list[tuple[str, Path]]:
        return [
            ("report-plugins/init.py", module_path / "__init__.py"),
            ("report-plugins/tests.py", tests_path / "test_plugin.py"),
        ]

    def get_plugin_type(self) -> str:
        return "report"

    def include_snakemake_dev_dependency(self) -> bool:
        return True
