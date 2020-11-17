#!/usr/bin/env python

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020, Vanessa SOchat"
__license__ = "MPL 2.0"

from snakedeploy.logger import setup_logger
from snakedeploy.providers import ProviderRunner
import snakedeploy
import argparse
import sys


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
        help="suppress additional output.",
        default=False,
        action="store_true",
    )

    deploy_group = parser.add_argument_group("DEPLOY")
    deploy_group.add_argument(
        "--create-remote",
        dest="template",
        help="Template the repository first to create a remote to clone. GITHUB_TOKEN is required.",
        default=False,
        action="store_true",
    )

    deploy_group.add_argument(
        "--name",
        dest="name",
        help="A custom name for your template repository, <org/username>/<repository>.",
    )

    # Logging
    logging_group = parser.add_argument_group("LOGGING")

    logging_group.add_argument(
        "--verbose",
        dest="verbose",
        help="verbose output for logging.",
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

    logging_group.add_argument(
        "--log-use-threads",
        dest="use_threads",
        action="store_true",
        help="Force threads rather than processes.",
    )

    parser.add_argument(
        "repo",
        nargs="?",
        help="Repository address and destination to deploy, e.g., <source> <dest>",
    )

    parser.add_argument(
        "dest",
        nargs="?",
        help="Path to clone the repository, should not exist.",
    )

    parser.add_argument(
        "--force",
        dest="force",
        help="If the folder exists, force overwrite, meaning remove and replace.",
        default=False,
        action="store_true",
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
        use_threads=args.use_threads,
    )

    # Instantiate and depoy the runner
    runner = ProviderRunner()

    # First template the repository, if desired
    repo = args.repo
    if args.template:
        repo = runner.template(source=args.repo, name=args.name)
    runner.deploy(source=repo, dest=args.dest, force=args.force)


if __name__ == "__main__":
    main()
