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
