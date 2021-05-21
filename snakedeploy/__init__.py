__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from .version import __version__

assert __version__

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions
