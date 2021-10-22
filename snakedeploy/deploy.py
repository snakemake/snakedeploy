import subprocess as sp
import tempfile
from pathlib import Path
import os
import shutil

from jinja2 import Environment, PackageLoader

from snakedeploy.providers import get_provider
from snakedeploy.logger import logger
from snakedeploy.exceptions import UserError


def deploy(source_url: str, name: str, tag: str, dest_path: Path, force=False):
    """Deploy a given workflow to the local machine, using the Snakemake module system."""
    provider = get_provider(source_url)
    env = Environment(loader=PackageLoader("snakedeploy"))
    template = env.get_template("use_module.smk.jinja")

    snakefile = dest_path / "workflow/Snakefile"
    if snakefile.exists() and not force:
        raise UserError(
            f"{snakefile} already exists, aborting (use --force to overwrite)"
        )
    dest_config = dest_path / "config"
    if dest_config.exists() and not force:
        raise UserError(
            f"{dest_config} already exists, aborting (use --force to overwrite)"
        )

    logger.info("Writing Snakefile with module definition...")
    os.makedirs(dest_path / "workflow", exist_ok=True)
    module_deployment = template.render(
        name=name or provider.get_repo_name().replace("-", "_"),
        snakefile=provider.get_source_file_declaration("workflow/Snakefile", tag),
        repo=source_url,
    )
    with open(snakefile, "w") as f:
        print(module_deployment, file=f)

    with tempfile.TemporaryDirectory() as tmpdir:
        logger.info("Obtaining source repository...")
        try:
            sp.run(["git", "clone", source_url, "."], cwd=tmpdir, check=True)
        except sp.CalledProcessError as e:
            raise UserError("Failed to clone repository {}:\n{}", source_url, e)
        config_dir = Path(tmpdir) / "config"
        no_config = not config_dir.exists()
        if no_config:
            logger.warning(
                "No config directory found in source repository. "
                "Please check whether the source repository really does not "
                "need or provide any configuration."
            )
            os.makedirs(dest_path / "config", exist_ok=True)
            dummy_config_file = dest_path / "config" / "config.yaml"
            if not dummy_config_file.exists():
                with open(dummy_config_file, "w"):
                    pass
        else:
            logger.info("Writing template configuration...")
            shutil.copytree(config_dir, dest_config, dirs_exist_ok=force)

    logger.info(
        env.get_template("post-instructions.txt.jinja").render(
            no_config=no_config, dest_path=dest_path
        )
    )
