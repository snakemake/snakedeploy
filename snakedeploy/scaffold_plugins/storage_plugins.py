from pathlib import Path
from typing import List, Tuple

from snakedeploy.scaffold_plugins.common import ScaffoldPlugin


class ScaffoldSnakemakeStoragePlugin(ScaffoldPlugin):
    def get_templates(
        self, module_path: Path, tests_path: Path
    ) -> List[Tuple[str, Path]]:
        return [
            ("storage-plugins/init.py", module_path / "__init__.py"),
            ("storage-plugins/tests.py", tests_path / "test_plugin.py"),
        ]

    def get_plugin_type(self) -> str:
        return "storage"

    def include_snakemake_dev_dependency(self) -> bool:
        return False
