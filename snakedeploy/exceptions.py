__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"


class MissingEnvironmentVariable(RuntimeError):
    """Thrown if a required environment variable is not provided."""

    def __init__(self, varname, *args, **kwargs):
        super(MissingEnvironmentVariable, self).__init__(*args, **kwargs)
        self.varname = varname

    def __str__(self):
        return "Missing environment variable '{}' is required".format(self.varname)


class DirectoryNotFoundError(FileNotFoundError):
    """Thrown if a directory is not found"""

    def __init__(self, dirname, reason, *args, **kwargs):
        super(DirectoryNotFoundError, self).__init__(*args, **kwargs)
        self.dirname = dirname
        self.reason = reason

    def __str__(self):
        return "{} {}.".format(self.dirname, self.reason)


class UnrecognizedProviderError(ValueError):
    """Thrown if an unrecognized provider is asked for"""

    def __init__(self, message, *args, **kwargs):
        super(UnrecognizedProviderError, self).__init__(*args, **kwargs)


class InvalidVersionSpec(ValueError):
    """Thrown if an invalid version spec is provided"""

    def __init__(self, vspec, message):
        super().__init__(f"Invalid version spec '{vspec}': {message}")


class UserError(ValueError):
    """An error that is presented as simple error message without a stack trace"""
