__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

__version__ = "0.8.3"
AUTHOR = "Vanessa Sochat"
AUTHOR_EMAIL = "vsochat@stanford.edu"
NAME = "snakedeploy"
PACKAGE_URL = "https://github.com/snakemake/snakedeploy"
KEYWORDS = "snakemake,pipeline,deployment"
DESCRIPTION = "Deploy a snakemake pipeline from GitHub"
LICENSE = "LICENSE"

################################################################################
# Global requirements

INSTALL_REQUIRES = (
    ("requests", {"min_version": None}),
    ("pandas", {"min_version": None}),
    ("jinja2", {"min_version": None}),
    ("pyyaml", {"min_version": None}),
    ("pygithub", {"min_version": None}),
    ("packaging", {"min_version": None}),
    ("reretry", {"min_version": None}),
)

TESTS_REQUIRES = (("pytest", {"min_version": "4.6.2"}),)


ALL_REQUIRES = INSTALL_REQUIRES
