from pathlib import Path
from typing import List, Tuple

from snakedeploy.scaffold_plugins.common import ScaffoldPlugin


class ScaffoldSnakemakeExecutorPlugin(ScaffoldPlugin):
    def get_templates(
        self, module_path: Path, tests_path: Path
    ) -> List[Tuple[str, Path]]:
        return [
            ("executor-plugins/init.py", module_path / "__init__.py"),
            ("executor-plugins/tests.py.j2", tests_path / "test_plugin.py"),
        ]

    def get_plugin_type(self) -> str:
        return "executor"

    def include_snakemake_dev_dependency(self) -> bool:
        return True
