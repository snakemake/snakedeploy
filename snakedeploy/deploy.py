import tempfile
from pathlib import Path
import os
import shutil

from jinja2 import Environment, PackageLoader

from snakedeploy.providers import get_provider
from snakedeploy.logger import logger
from snakedeploy.exceptions import UserError


class WorkflowDeployer:
    def __init__(self, source: str, dest: Path, force=False):
        self.provider = get_provider(source)
        self.env = Environment(loader=PackageLoader("snakedeploy"))
        self.dest_path = dest
        self.force = force

    @property
    def snakefile(self):
        return self.dest_path / "workflow/Snakefile"

    @property
    def config(self):
        return self.dest_path / "config"

    def deploy_config(self, tmpdir: str):
        """
        Deploy the config directory, either using an existing or creating a dummy.

        returns a boolean "no_config" to indicate if there is not a config (True)
        """
        # Handle the config/
        config_dir = Path(tmpdir) / "config"
        no_config = not config_dir.exists()
        if no_config:
            logger.warning(
                "No config directory found in source repository. "
                "Please check whether the source repository really does not "
                "need or provide any configuration."
            )

            # This will fail running the workflow if left empty
            os.makedirs(self.dest_path / "config", exist_ok=True)
            dummy_config_file = self.dest_path / "config" / "config.yaml"
            if not dummy_config_file.exists():
                with open(dummy_config_file, "w"):
                    pass
        else:
            logger.info("Writing template configuration...")
            shutil.copytree(config_dir, self.config, dirs_exist_ok=self.force)
        return no_config

    def deploy(self, name: str, tag: str, branch: str):
        """
        Deploy a source to a destination.
        """
        self.check()

        # Create a temporary directory to grab config directory and snakefile
        with tempfile.TemporaryDirectory() as tmpdir:
            logger.info("Obtaining source repository...")

            # Clone temporary directory to find assets
            self.provider.clone(tmpdir)

            # Either copy existing config or create a dummy config
            no_config = self.deploy_config(tmpdir)

            # Inspect repository to find existing snakefile
            self.deploy_snakefile(tmpdir, name, tag, branch)

        logger.info(
            self.env.get_template("post-instructions.txt.jinja").render(
                no_config=no_config, dest_path=self.dest_path
            )
        )

    def check(self):
        """
        Check to ensure we haven't already deployed to the destination.
        """
        if self.snakefile.exists() and not self.force:
            raise UserError(
                f"{self.snakefile} already exists, aborting (use --force to overwrite)"
            )

        if self.config.exists() and not self.force:
            raise UserError(
                f"{self.config} already exists, aborting (use --force to overwrite)"
            )

    def deploy_snakefile(self, tmpdir: str, name: str, tag: str, branch: str):
        """
        Deploy the Snakefile to workflow/Snakefile
        """
        # The name cannot have -
        name = name or self.provider.get_repo_name()
        name = name.replace("-", "_")

        snakefile_path = Path(tmpdir) / "workflow" / "Snakefile"
        snakefile = os.path.join("workflow", "Snakefile")
        if not snakefile_path.exists():

            # Either we allow this or fail workflow here if it's not possible
            logger.warning(
                "Snakefile path not found in traditional path %s, workflow may be error prone."
                % snakefile_path
            )
            snakefile_path = Path(tmpdir) / "Snakefile"
            snakefile = "Snakefile"
            if not snakefile_path.exists():
                raise UserError(
                    "No Snakefile was found at root or in workflow directory."
                )

        template = self.env.get_template("use_module.smk.jinja")
        logger.info("Writing Snakefile with module definition...")
        os.makedirs(self.dest_path / "workflow", exist_ok=True)
        module_deployment = template.render(
            name=name,
            snakefile=self.provider.get_source_file_declaration(snakefile, tag, branch),
            repo=self.provider.source_url,
        )
        with open(self.snakefile, "w") as f:
            print(module_deployment, file=f)


def deploy(
    source_url: str, name: str, tag: str, branch: str, dest_path: Path, force=False
):
    """
    Deploy a given workflow to the local machine, using the Snakemake module system.
    """
    sd = WorkflowDeployer(source=source_url, dest=dest_path, force=force)
    sd.deploy(name=name, tag=tag, branch=branch)
