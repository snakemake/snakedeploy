"""

Copyright (C) 2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

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
