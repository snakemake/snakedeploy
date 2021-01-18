#!/usr/bin/env python

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020, Vanessa SOchat"
__license__ = "MPL 2.0"

from snakedeploy.logger import setup_logger
from snakedeploy.providers import ProviderRunner
from snakedeploy.collect_files import collect_files
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

    subparsers = parser.add_subparsers(title="Subcommands", dest="subcommand")

    deploy_workflow_parser = subparsers.add_parser("deploy-workflow", help="Deploy a workflow from a git repository.")

    deploy_group = deploy_workflow_parser.add_argument_group("DEPLOY")
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

    deploy_workflow_parser.add_argument(
        "repo",
        nargs="?",
        help="Repository address and destination to deploy, e.g., <source> <dest>",
    )

    deploy_workflow_parser.add_argument(
        "dest",
        nargs="?",
        help="Path to clone the repository, should not exist.",
    )

    deploy_workflow_parser.add_argument(
        "--force",
        dest="force",
        help="If the folder exists, force overwrite, meaning remove and replace.",
        default=False,
        action="store_true",
    )

    collect_files = subparsers.add_parser(
        "collect-files", 
        help="""
        Collect files into a tabular structure, given input from STDIN that formats a glob pattern.
        """
    )
    collect_files.add_argument(
        "--input-pattern",
        default="^(?P<id>.+)$",
        help="A regex pattern to infer arguments for the file pattern."
    )
    collect_files.add_argument(
        "--glob-pattern",
        help="Glob pattern for collecting files. "
        "Can contain format information (according to the "
        "Python format minilanguage) that is filled by the input from STDIN. "
        "All matched files for one STDIN input are printed tab separated to one line, "
        "together with the STDIN input."
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

    try:
        if args.subcommand == "deploy-workflow":
            # Instantiate and depoy the runner
            runner = ProviderRunner()

            # First template the repository, if desired
            repo = args.repo
            if args.template:
                repo = runner.template(source=args.repo, name=args.name)
            runner.deploy(source=repo, dest=args.dest, force=args.force)
        elif args.subcommand == "collect-files":
            collect_files(input_pattern=args.input_pattern, glob_pattern=args.glob_pattern)
    except UserError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
