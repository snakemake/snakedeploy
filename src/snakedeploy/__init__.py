__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.0.0"  # Fallback when not installed properly

assert __version__
