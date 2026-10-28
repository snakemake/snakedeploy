__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"


class MissingEnvironmentVariable(RuntimeError):
    """Thrown if a required environment variable is not provided."""

    def __init__(self, varname, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.varname = varname

    def __str__(self):
        return f"Missing environment variable '{self.varname}' is required"


class DirectoryNotFoundError(FileNotFoundError):
    """Thrown if a directory is not found"""

    def __init__(self, dirname, reason, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dirname = dirname
        self.reason = reason

    def __str__(self):
        return f"{self.dirname} {self.reason}."


class UnrecognizedProviderError(ValueError):
    """Thrown if an unrecognized provider is asked for"""

    def __init__(self, message, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InvalidVersionSpec(ValueError):
    """Thrown if an invalid version spec is provided"""

    def __init__(self, vspec, message):
        super().__init__(f"Invalid version spec '{vspec}': {message}")


class UserError(ValueError):
    """An error that is presented as simple error message without a stack trace"""

    def __init__(self, message: str = "", suberrors: list | None = None):
        if message is not None:
            message = str(message)
        if suberrors is not None:
            if message:
                message = f"{message.strip()}:\n"
            message += "\n".join(str(err) for err in suberrors)
        super().__init__(message)


class UnsatisfiedCondaConstraintsError(UserError):
    """Thrown if there are unsatisfied conda constraints"""

    def __init__(self, unsatisfied_constraints, conda_env_path):
        details = ", ".join(
            f"{package}{version_spec.spec}"
            for package, version_spec in unsatisfied_constraints
        )
        super().__init__(
            f"Could not satisfy --ensure constraints for {conda_env_path}: {details}."
        )
