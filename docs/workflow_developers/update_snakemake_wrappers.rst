.. _update_snakemake_wrappers:

=========================
Update Snakemake wrappers
=========================

Snakedeploy can be used to automatically update the versions of Snakemake wrappers in a workflow.
Given that your workflow snakefiles are located e.g. under ``workflow/Snakefile`` (main entrypoint) and ``workflow/rules/``, this is done by executing

.. code:: console

    $ snakedeploy update-snakemake-wrappers workflow/Snakefile workflow/rules/*.smk

Snakedeploy will then

1. detemine the latest Snakemake wrapper release version,
2. find all rules in the given snakefiles that use a Snakemake wrapper,
3. set the wrapper release version in each of those rules to that latest version.

For details and additional options, run

.. code:: console

    $ snakedeploy update-snakemake-wrappers --help