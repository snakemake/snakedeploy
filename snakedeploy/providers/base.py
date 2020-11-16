__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020, Vanessa SOchat"
__license__ = "MPL 2.0"

import abc


class ProviderBase:
    """A snakedeploy provider is a resource to retrieve a pipeline."""

    name = "base"

    @abc.abstractmethod
    def clone(self, source, dest, force=False):
        """The clone method should be implemented by the subclass, and result
        in a repository source being copied to a destination,
        """
        raise NotImplementedError
