#!/usr/bin/env python

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

import argparse
import sys
from pathlib import Path
from snakedeploy.conda import pin_conda_envs, update_conda_envs

from snakedeploy.logger import setup_logger
from snakedeploy.deploy import deploy
from snakedeploy.collect_files import collect_files
import snakedeploy
from snakedeploy.exceptions import UserError
from .snakemake_wrappers import update_snakemake_wrappers


def get_parser():
    parser = argparse.ArgumentParser(
        description="Snakedeploy: deploy snakemake pipelines from version control."
    )

    parser.add_argument(
        "--version",
        dest="version",
        help="print the version and exit.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--quiet",
        dest="quiet",
        help="Minimize output.",
        default=False,
        action="store_true",
    )

    # Logging
    logging_group = parser.add_argument_group("LOGGING")

    logging_group.add_argument(
        "--verbose",
        dest="verbose",
        help="Verbose output.",
        default=False,
        action="store_true",
    )

    logging_group.add_argument(
        "--log-disable-color",
        dest="disable_color",
        default=False,
        help="Disable color for snakedeploy logging.",
        action="store_true",
    )

    subparsers = parser.add_subparsers(title="Subcommands", dest="subcommand")

    deploy_workflow_parser = subparsers.add_parser(
        "deploy-workflow", description="Deploy a workflow from a git repository."
    )

    deploy_group = deploy_workflow_parser.add_argument_group("DEPLOY")

    deploy_workflow_parser.add_argument(
        "repo",
        help="Workflow repository to use.",
    )

    deploy_workflow_parser.add_argument(
        "dest",
        help="Path to create the deploying workflow in.",
    )

    deploy_workflow_parser.add_argument(
        "--tag",
        help="Git tag to deploy from (e.g. a certain release).",
    )

    deploy_workflow_parser.add_argument(
        "--branch",
        help="Git branch to deploy from.",
    )

    deploy_group.add_argument(
        "--name",
        help="The name for the module in the resulting Snakefile (default: repository name).",
    )

    deploy_workflow_parser.add_argument(
        "--force",
        action="store_true",
        help="Enforce overwriting of already present files.",
    )

    collect_files = subparsers.add_parser(
        "collect-files",
        description="Collect files into a tabular structure, given input from "
        "STDIN formats glob patterns defined in a config sheet.",
    )
    collect_files.add_argument(
        "config",
        help="A TSV file containing two columns input_pattern and glob_pattern. "
        "The input pattern is a Python regular expression that selects lines from STDIN, "
        "and extracts values from it (as groups; example: 'S888_Nr(?P<nr>[0-9]+)'). "
        "If possible such extracted values are automatically converted to integers. "
        "The glob pattern is formatted (via the Python format minilanguage) with the values from the "
        "input pattern and used to glob files from the filesystem. "
        "The globbed files are printed as TSV next to the matching input value taken from STDIN. "
        "If the globbing does not return any files for one STDIN input, an error is thrown. "
        "If one STDIN input is not matched by any of the provided stdin patterns, an error is thrown. "
        "If one STDIN input is matched by multiple of the provided stdin patterns, an error is thrown.",
    )

    pin_conda_envs = subparsers.add_parser(
        "pin-conda-envs",
        description="Pin given conda environment definition files (in YAML format) "
        "into a list of explicit package URLs including checksums, stored in a file "
        "<prefix>.<platform>.pin.txt with prefix being the path to the original definition file and "
        "<platform> being the name of the platform the pinning was performed on (e.g. linux-64). "
        "The resulting file will be automatically used by Snakemake to restore exactly the pinned "
        "environment. Also you can use it manually, e.g. with 'mamba create -f <path-to-pin-file> -n <env-name>'.",
    )
    pin_conda_envs.add_argument(
        "envfiles", nargs="+", help="Environment definition YAML files to pin."
    )
    pin_conda_envs.add_argument(
        "--conda-frontend",
        choices=["mamba", "conda"],
        default="mamba",
        help="Conda frontend to use (default: mamba).",
    )

    update_conda_envs = subparsers.add_parser(
        "update-conda-envs",
        description="Update given conda environment definition files (in YAML format) "
        "so that all contained packages are set to the latest feasible versions.",
    )
    update_conda_envs.add_argument(
        "envfiles", nargs="+", help="Environment definition YAML files to update."
    )
    update_conda_envs.add_argument(
        "--conda-frontend",
        choices=["mamba", "conda"],
        default="mamba",
        help="Conda frontend to use (default: mamba).",
    )
    update_conda_envs.add_argument(
        "--pin-envs",
        action="store_true",
        help="also pin the updated environments (see pin-conda-envs subcommand).",
    )
    update_conda_envs.add_argument(
        "--create-prs",
        action="store_true",
        help="Create pull request for each updated environment. "
        "Requires GITHUB_TOKEN and GITHUB_REPOSITORY (the repo name) and one of GITHUB_REF_NAME or GITHUB_BASE_REF "
        "(preferring the latter, representing the target branch, e.g. main or master) environment "
        "variables to be set (the latter three are available when running as github action). "
        "In order to enable further actions (e.g. checks) to run on the generated PRs, the "
        "provided GITHUB_TOKEN may not be the default github actions token. See here for "
        "options: https://github.com/peter-evans/create-pull-request/blob/main/docs/concepts-guidelines.md#triggering-further-workflow-runs.",
    )
    update_conda_envs.add_argument(
        "--entity-regex",
        help="Regular expression for deriving an entity name from the environment file name "
        "(will be used for adding a label and for title and description). Has to contain a group 'entity' "
        "(e.g. '(?P<entity>.+)/environment.yaml').",
    )
    update_conda_envs.add_argument(
        "--pr-add-label",
        action="store_true",
        help="Add a label to the PR. Has to be used in combination with --entity-regex.",
    )
    update_conda_envs.add_argument(
        "--warn-on-error",
        action="store_true",
        help="Only warn if conda env evaluation fails and go on with the other envs.",
    )

    update_snakemake_wrappers = subparsers.add_parser(
        "update-snakemake-wrappers",
        description="Update all snakemake wrappers in given Snakefiles.",
    )
    update_snakemake_wrappers.add_argument(
        "snakefiles", nargs="+", help="Paths to Snakefiles which should be updated."
    )
    update_snakemake_wrappers.add_argument(
        "--git-ref",
        help="Git reference to use for updating the wrappers (e.g. a snakemake-wrapper release). "
        "If nothing specified, the latest release will be used.",
    )

    return parser


def main():
    """main entrypoint for snakedeploy"""
    parser = get_parser()

    def help(return_code=0):
        """print help, including the software version and active client
        and exit with return code.
        """
        version = snakedeploy.__version__

        print("\nSnakeDeploy Python v%s" % version)
        parser.print_help()
        sys.exit(return_code)

    # If the user didn't provide both arguments, show the full help
    if len(sys.argv) < 2:
        help()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    # Show the version and exit
    if args.version:
        print(snakedeploy.__version__)
        sys.exit(0)

    setup_logger(
        quiet=args.quiet,
        nocolor=args.disable_color,
        debug=args.verbose,
    )
    from snakedeploy.logger import logger

    try:
        if args.subcommand == "deploy-workflow":
            if not (args.tag or args.branch):
                raise UserError("Please specify either --tag or --branch")
            deploy(
                args.repo,
                name=args.name,
                tag=args.tag,
                branch=args.branch,
                dest_path=Path(args.dest),
                force=args.force,
            )
        elif args.subcommand == "collect-files":
            collect_files(config_sheet_path=args.config)
        elif args.subcommand == "pin-conda-envs":
            pin_conda_envs(
                args.envfiles,
                conda_frontend=args.conda_frontend,
            )
        elif args.subcommand == "update-conda-envs":
            update_conda_envs(
                args.envfiles,
                conda_frontend=args.conda_frontend,
                create_prs=args.create_prs,
                pin_envs=args.pin_envs,
                entity_regex=args.entity_regex,
                pr_add_label=args.pr_add_label,
                warn_on_error=args.warn_on_error,
            )
        elif args.subcommand == "update-snakemake-wrappers":
            update_snakemake_wrappers(args.snakefiles, git_ref=args.git_ref)
    except UserError as e:
        logger.error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
