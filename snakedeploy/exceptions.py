__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020, Vanessa SOchat"
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
