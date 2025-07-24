from pathlib import Path
from typing import List, Tuple

from snakedeploy.scaffold_plugins.common import ScaffoldPlugin


class ScaffoldSnakemakeSoftwareDeploymentPlugin(ScaffoldPlugin):
    def get_templates(
        self, module_path: Path, tests_path: Path
    ) -> List[Tuple[str, Path]]:
        return [
            ("software-deployment-plugins/init.py", module_path / "__init__.py"),
            ("software-deployment-plugins/tests.py", tests_path / "test_plugin.py"),
        ]

    def get_plugin_type(self) -> str:
        return "software-deployment"

    def include_snakemake_dev_dependency(self) -> bool:
        return False
