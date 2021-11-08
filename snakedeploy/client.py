#!/usr/bin/env python

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

import argparse
import sys
from pathlib import Path

from snakedeploy.logger import setup_logger
from snakedeploy.deploy import deploy
from snakedeploy.collect_files import collect_files
import snakedeploy
from snakedeploy.exceptions import UserError


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
        required=True,
        help="Git tag (or branch) to deploy from (e.g. a certain release).",
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
            deploy(
                args.repo,
                name=args.name,
                tag=args.tag,
                dest_path=Path(args.dest),
                force=args.force,
            )
        elif args.subcommand == "collect-files":
            collect_files(config_sheet_path=args.config)
    except UserError as e:
        logger.error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
