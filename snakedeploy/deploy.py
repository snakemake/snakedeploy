import glob
import tempfile
from pathlib import Path
import os
import shutil
from typing import Dict, Optional

from jinja2 import Environment, PackageLoader
import yaml

from snakedeploy.providers import get_provider
from snakedeploy.logger import logger
from snakedeploy.exceptions import UserError


class WorkflowDeployer:
    def __init__(
        self,
        source: str,
        dest: Path,
        tag: Optional[str] = None,
        branch: Optional[str] = None,
        force=False,
    ):
        self.provider = get_provider(source)
        self.env = Environment(loader=PackageLoader("snakedeploy"))
        self.dest_path = dest
        self.force = force
        self._cloned = None
        self.tag = tag
        self.branch = branch

    def __enter__(self):
        return self

    def __exit__(self, exc, value, tb):
        self._cloned.cleanup()

    @property
    def snakefile(self):
        return self.dest_path / "workflow/Snakefile"

    @property
    def config(self):
        return self.dest_path / "config"

    @property
    def profiles(self):
        return self.dest_path / "profiles"

    def deploy_config(self):
        """
        Deploy the config directory, either using an existing or creating a dummy.

        returns a boolean "no_config" to indicate if there is not a config (True)
        """
        # Handle the config/
        config_dir = Path(self.repo_clone) / "config"
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

    def deploy_profile(self):
        """
        Deploy the profile directory if it exists

        returns a boolean "no_profile" to indicate if there is not a profile (True)
        """
        # Handle the profile/
        profile_dir = Path(self.repo_clone) / "profiles"
        no_profile = not profile_dir.exists()
        if no_profile:
            logger.warning(
                "No profile directory found in source repository. "
                "Please check whether the source repository really does not "
                "need or provide any profiles."
            )
        else:
            logger.info("Writing template profiles")
            shutil.copytree(profile_dir, self.profiles, dirs_exist_ok=self.force)
        return no_profile

    def deploy_license(self):
        """
        Deploy the license file if it exists

        returns a boolean "no_license" to indicate if there is no license (True)
        """
        # List possible license file names and extensions
        license_variants = [
            "license*",
            "License*",
            "LICENSE*",
            "licence*",
            "Licence*",
            "LICENCE*",
        ]
        licenses = []  # licenses found

        # Iterate over the variants and check if a license file exists in the directory
        for variant in license_variants:
            # Use glob to match files with any extension
            matching_files = glob.glob(os.path.join(self.repo_clone, variant))
            if matching_files:
                licenses.extend(matching_files)

        license_file = Path(licenses[0]) if len(licenses) != 0 else None
        if license_file is None:
            no_license = True
        else:
            no_license = not license_file.exists()

        if no_license:
            pass
        else:
            logger.info("Writing license")
            shutil.copy(license_file, self.dest_path)
        return no_license

    @property
    def repo_clone(self):
        if self._cloned is None:
            logger.info("Obtaining source repository...")
            self._cloned = tempfile.TemporaryDirectory()
            self.provider.clone(self._cloned.name)
            if self.tag is not None:
                self.provider.checkout(self._cloned.name, self.tag)
            elif self.branch is not None:
                self.provider.checkout(self._cloned.name, self.branch)

        return self._cloned.name

    def deploy(self, name: str):
        """
        Deploy a source to a destination.
        """
        self.check()

        # Either copy existing config or create a dummy config
        no_config = self.deploy_config()

        # Copy profile directory if it exists, see issue #64
        self.deploy_profile()

        # Copy license if it exists
        self.deploy_license()

        # Inspect repository to find existing snakefile
        self.deploy_snakefile(self.repo_clone, name)

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

        if self.profiles.exists() and not self.force:
            raise UserError(
                f"{self.profiles} already exists, aborting (use --force to overwrite)"
            )

    def deploy_snakefile(self, tmpdir: str, name: str):
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

        # fixes #80: Also consider config.yml as name for configuration file
        config_path = Path(tmpdir) / "config" / "config.yaml"
        config = os.path.join("config", "config.yaml")
        if not config_path.exists():
            config_path = Path(tmpdir) / "config" / "config.yml"
            config = os.path.join("config", "config.yml")
            if not config_path.exists():
                # Neither config.yaml nor config.yml exists, stick to the default.
                config = os.path.join("config", "config.yaml")

        template = self.env.get_template("use_module.smk.jinja")
        logger.info("Writing Snakefile with module definition...")
        os.makedirs(self.dest_path / "workflow", exist_ok=True)
        module_deployment = template.render(
            name=name,
            snakefile=self.provider.get_source_file_declaration(
                snakefile, self.tag, self.branch
            ),
            repo=self.provider.source_url,
            config=config,
        )
        with open(self.snakefile, "w") as f:
            print(module_deployment, file=f)

    def get_json_schema(self, item: str) -> Optional[Dict]:
        """Get schema under workflow/schemas/{item}.schema.{yaml|yml|json} as
        python dict."""
        clone = Path(self.repo_clone)
        for ext in ["yaml", "yml", "json"]:
            path = clone / "workflow" / "schemas" / f"{item}.schema.{ext}"
            if path.exists():
                return yaml.safe_load(path.read_text())
        return None


def deploy(
    source_url: str,
    name: Optional[str],
    tag: Optional[str],
    branch: Optional[str],
    dest_path: Path,
    force=False,
):
    """
    Deploy a given workflow to the local machine, using the Snakemake module system.
    """
    with WorkflowDeployer(
        source=source_url, dest=dest_path, tag=tag, branch=branch, force=force
    ) as sd:
        sd.deploy(name=name)
