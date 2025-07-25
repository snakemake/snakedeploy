from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Tuple
import subprocess as sp
from jinja2 import Environment, PackageLoader, select_autoescape
import toml

from snakedeploy.exceptions import UserError


class ScaffoldPlugin(ABC):
    @abstractmethod
    def get_templates(
        self, module_path: Path, tests_path: Path
    ) -> List[Tuple[str, Path]]: ...

    @abstractmethod
    def get_plugin_type(self) -> str: ...

    def get_dependencies(self) -> List[str]:
        return [f"snakemake-interface-{self.get_plugin_type()}-plugins"]

    @abstractmethod
    def include_snakemake_dev_dependency(self) -> bool: ...

    def get_package_name_prefix(self) -> str:
        return f"snakemake-{self.get_plugin_type()}-plugin-"

    def handle(self) -> None:
        def load_pyproject() -> Dict[str, Any]:
            try:
                with open("pyproject.toml", "r") as f:
                    return toml.load(f)
            except FileNotFoundError:
                raise UserError("pyproject.toml not found in current directory")
            except Exception as e:
                raise UserError(f"Failed to read pyproject.toml: {e}") from e

        def save_pyproject(pyproject):
            try:
                with open("pyproject.toml", "w") as f:
                    toml.dump(pyproject, f)
            except Exception as e:
                raise UserError(f"Failed to write pyproject.toml: {e}") from e

        pyproject = load_pyproject()

        package_name = pyproject["project"]["name"]

        if not package_name.startswith(self.get_package_name_prefix()):
            raise UserError(
                f"Package name must start with {self.get_package_name_prefix()} "
                f"(found {package_name})"
            )

        plugin_name = package_name.replace(self.get_package_name_prefix(), "")

        if "urls" not in pyproject["project"]:
            pyproject["project"]["urls"] = {}
        pyproject["project"]["urls"]["Repository"] = "https://github.com/your/plugin"
        pyproject["project"]["urls"]["Documentation"] = (
            "https://snakemake.github.io/snakemake-plugin-catalog/plugins/"
            f"{self.get_plugin_type()}/{plugin_name}.html"
        )
        # the python dependency should be in line with the dependencies
        pyproject["project"]["requires-python"] = ">=3.11,<4.0"

        save_pyproject(pyproject)

        # add dependencies
        sp.run(
            ["pixi", "add", "--pypi", "snakemake-interface-common"]
            + self.get_dependencies()
        )
        dev_deps = [
            "pixi",
            "add",
            "--pypi",
            "--feature",
            "dev",
            "ruff",
            "coverage",
            "pytest",
            "twine",
            "python-build",
        ]
        if self.include_snakemake_dev_dependency():
            dev_deps.append("snakemake")
        sp.run(dev_deps, check=True)

        pyproject = load_pyproject()
        pyproject["tool"]["pixi"]["environments"] = {"dev": {"features": ["dev"]}}
        save_pyproject(pyproject)

        sp.run(
            ["pixi", "task", "add", "--feature", "dev", "lint", "ruff check"],
            check=True,
        )
        sp.run(
            ["pixi", "task", "add", "--feature", "dev", "format", "ruff format"],
            check=True,
        )
        sp.run(
            [
                "pixi",
                "task",
                "add",
                "--feature",
                "dev",
                "test",
                "pytest "
                f"--cov={package_name} "
                "--cov-report=xml:coverage-report/coverage.xml "
                "--cov-report=term-missing "
                "tests/tests.py",
            ],
            check=True,
        )
        sp.run(
            ["pixi", "task", "add", "--feature", "dev", "build", "python -m build"],
            check=True,
        )
        sp.run(
            [
                "pixi",
                "task",
                "add",
                "--feature",
                "dev",
                "check-build",
                "python -m twine check dist/*",
                "--depends-on",
                "build",
            ],
            check=True,
        )

        # add skeleton code
        templates = Environment(
            loader=PackageLoader("snakedeploy"),
            autoescape=select_autoescape(),
            keep_trailing_newline=True,
        )

        def render_template(name, dest: Path):
            dest.parent.mkdir(exist_ok=True, parents=True)
            with open(dest, "w") as f:
                f.write(
                    templates.get_template("plugins/" + name).render(
                        pyproject=pyproject, plugin_name=plugin_name
                    )
                )

        module_path = Path("src") / pyproject["project"]["name"].replace("-", "_")
        tests_path = Path("tests")
        workflows_path = Path(".github/workflows")

        (tests_path / "__init__.py").unlink(missing_ok=True)

        render_template("setup.cfg.j2", Path("setup.cfg"))
        render_template("release_please.yml.j2", workflows_path / "release-please.yml")
        render_template("ci.yml.j2", workflows_path / "ci.yml")
        render_template(
            "conventional_prs.yml.j2", workflows_path / "conventional-prs.yml"
        )

        for template, target in self.get_templates(
            module_path=module_path, tests_path=tests_path
        ):
            render_template(template, target)
