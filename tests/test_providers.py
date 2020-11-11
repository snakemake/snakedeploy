#!/usr/bin/env python
"""

Copyright (C) 2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

import os
import pytest
from snakedeploy.providers import ProviderRunner
from snakedeploy.exceptions import UnrecognizedProviderError


def test_github_provider(tmp_path):
    """test the GitHub provider."""
    provider = ProviderRunner()
    dest = os.path.join(str(tmp_path), "github-test")
    assert not os.path.exists(dest)

    # Case 1: an invalid URL should raise an error
    with pytest.raises(UnrecognizedProviderError):
        provider.deploy("https://nothub.com/repository/address", dest)
    assert not os.path.exists(dest)

    # Case 2: a valid URL should work
    provider.deploy(
        "https://github.com/snakemake-workflows/dna-seq-varlociraptor", dest
    )
    assert os.path.exists(dest)

    # make sure expected files are present
    for filename in ["README.md", "LICENSE"]:
        assert os.path.exists(os.path.join(dest, filename))

    # Case 3: A new deploy should not work
    with pytest.raises(SystemExit):
        provider.deploy(
            "https://github.com/snakemake-workflows/dna-seq-varlociraptor", dest
        )

    # Case 4: A new deploy with force should work
    provider.deploy(
        "https://github.com/snakemake-workflows/dna-seq-varlociraptor", dest, force=True
    )
