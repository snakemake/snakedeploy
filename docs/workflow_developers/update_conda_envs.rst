.. _update_conda_envs:

==============================
Update conda environment files
==============================

Snakedeploy can be used to automatically update a set of given conda environment files to the latest feasible versions of the packages they contain.
Given that the conda environments you want to update are located e.g. under ``workflow/envs``, this is done by executing

.. code:: console

    $ snakedeploy update-conda-envs workflow/envs/*.yaml

Snakedeploy will 

1. internally remove the version constraints of the packages given in each selected environment file, 
2. determine the latest feasible combination of the versions, 
3. and update the environment file with corresponding pinned versions.

For details and additional options, run

.. code:: console

    $ snakedeploy update-conda-envs --help

.. _pin_conda_envs:

===========================
Pin/lock conda environments
===========================

Snakedeploy can also pin the conda environment files to concrete package urls of not only the packages mentioned in the environment files but also all of their dependencies.
This way, next time Snakemake deploys the environments, it will not use the actual conda environment files but the pin file with the concrete package urls of all dependencies.
This is like a frozen snapshot of the environment at the time of pinning.

To pin the conda environment files, either run above command with the ``--pin-envs`` option:

.. code:: console

    $ snakedeploy update-conda-envs workflow/envs/*.yaml --pin-envs

Or use the ``pin-conda-envs`` command after updating the conda environment files:

.. code:: console

    $ snakedeploy pin-conda-envs workflow/envs/*.yaml

==============================================
Ensuring auxiliary package version constraints
==============================================

Use ``--ensure`` to require package versions to satisfy one or more Conda
version constraints. The constraints are checked against the resolved
environment. If the resulting environment does not satisfy them, the command
fails with an error.

Constraints use a package name
followed by a Conda version specifier; quote specs containing operators so
the shell does not interpret them. Specify the option once per constraint:

.. code:: console

    $ snakedeploy pin-conda-envs workflow/envs/*.yaml --ensure 'python>=3.12' 'numpy>=2'

By default, pinning is updated whenever ``pin-conda-envs`` is run. Add
``--only-if-ensure-is-unsatisfied`` to skip re-pinning when an existing pin
already satisfies all supplied ``--ensure`` constraints. If a constraint is
unsatisfied (or there is no pin file to check), the environment is resolved
and pinned, and the constraints are checked again. The flag is also available
for ``update-conda-envs``; there, the environment is only updated if its
currently resolved versions do not satisfy the constraints. For example:

.. code:: console

    $ snakedeploy pin-conda-envs workflow/envs/*.yaml --ensure 'python>=3.12' --only-if-ensure-is-unsatisfied
    $ snakedeploy update-conda-envs workflow/envs/*.yaml --ensure 'python>=3.12' --only-if-ensure-is-unsatisfied

This can be helpful to e.g. ensure that all environments are safe.
For example, to ensure that all environment pins are safe with respect to the Python [emudhra issue](https://discuss.python.org/t/information-for-python-users-regarding-emudhra-emsign-ca-certificate-security-incident/109576), run:

.. code:: console

    $ snakedeploy pin-conda-envs */*/environment.yaml */*/*/environment.yaml --ensure "certify>=2026.10.19" "pip>=26.2.2" "uv>=0.13.4" "sigstore>=4.5.1" "pixi>=0.82.1" "conda>=26.9.4" --only-if-ensure-is-unsatisfied

If any environment pin does not satisfy the specified constraints, the command will fail with an error, indicating which constraints were not met.
You can then follow-up with ``snakedeploy update-conda-envs`` of the respective environment files, again using the same ``--ensure`` constraints, which will hopefully finally comply with the constraints.