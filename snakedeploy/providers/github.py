"""

Copyright (C) 2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

import os
import sys
import shutil
from snakedeploy.utils import run_command


class GitHubProvider:
    """A snakedeploy provider is a resource to retrieve a pipeline."""

    name = "github"
    matchstring = "github"

    def check_install(self):
        """A helper to ensure that git is installed, returns False if not."""
        cmd = ["git", "--version"]
        try:
            result = run_command(cmd, quiet=True)
            return result.get("return_code", 1) == 0
        except:
            return False

    def clone(self, source, dest, force=False):
        """Clone a repository to a destination, force overwriting if necessary."""
        if os.path.exists(dest) and not force:
            sys.exit(f"{dest} exists and force is set to False, will not overwrite.")
        elif os.path.exists(dest) and force:
            shutil.rmtree(dest)
        if not self.check_install():
            sys.exit("git not found on the path, install it to continue.")

        # Use simple Git command
        return_code = os.system(f"git clone {source} {dest}")
        if return_code == 0:
            return dest
        sys.exit(f"Error cloning repository: {return_code}")
