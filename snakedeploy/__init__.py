__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from .version import __version__

assert __version__

from snakedeploy.deploy import deploy
from snakedeploy.collect_files import collect_files