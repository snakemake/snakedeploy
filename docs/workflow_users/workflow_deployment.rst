.. _deploy:

================
Deploy workflows
================

Snakedeploy enables you to automatically deploy a workflow from a public git repository to your local machine, by using Snakemake's module system.
This way, public workflow can be used and configured for your data.
For example, you can use this in combination with the standardized Snakemake workflows avalailable in the `Snakemake workflow catalog <https://snakemake.github.io/snakemake-workflow-catalog/docs/all_standardized_workflows.html>`__.
Via the command line, deployment works as follows:

.. code-block:: console

    $ snakedeploy deploy-workflow https://github.com/snakemake-workflows/dna-seq-varlociraptor /tmp/dest --tag v1.0.0


Snakedeploy will then generate a workflow definition ``/tmp/dest/workflow/Snakefile`` that declares the given workflow as a module.
For the example above, it will have the following content


.. code-block:: python

    configfile: "config/config.yaml"


    # declare https://github.com/snakemake-workflows/dna-seq-varlociraptor as a module
    module dna_seq_varlociraptor:
        snakefile: 
            github("snakemake-workflows/dna-seq-varlociraptor", path="workflow/Snakefile", tag="v1.0.0")
        config:
            config


    # use all rules from https://github.com/snakemake-workflows/dna-seq-varlociraptor
    use rule * from dna_seq_varlociraptor

utilizing `Snakemake's module system <https://snakemake.readthedocs.io/en/stable/snakefiles/deployment.html#using-and-combining-pre-exising-workflows>`__.
In addition, it will copy over the ``config/`` and ``profiles/`` directories of the given repository (and their contents) into respective directories under ``/tmp/dest/``.
These should be seen as templates, and can be modified according to your needs.
Further, the workflow definition Snakefile can be arbitrarily extended and modified, thereby making any changes to the used workflow transparent (also see the `snakemake module documentation <https://snakemake.readthedocs.io/en/stable/snakefiles/modularization.html#snakefiles-modules>`_).

It is highly advisable to put the deployed workflow into a new (perhaps private) git repository (e.g., see `here <https://docs.github.com/en/github/importing-your-projects-to-github/adding-an-existing-project-to-github-using-the-command-line>`_ for instructions how to do that with Github).

If you want to pin the deployment to an exact commit (e.g. for full reproducibility independent of any future changes to a branch or tag), use ``--commit`` instead of (or in addition to) ``--tag``/``--branch``:

.. code-block:: console

    $ snakedeploy deploy-workflow https://github.com/snakemake-workflows/dna-seq-varlociraptor /tmp/dest --branch main --commit 87709354b54391aee5dbb01a64cacfc20aed5ec3

This will generate a module declaration pinned to that exact commit:

.. code-block:: python

    module dna_seq_varlociraptor:
        snakefile:
            github("snakemake-workflows/dna-seq-varlociraptor", path="workflow/Snakefile", commit="87709354b54391aee5dbb01a64cacfc20aed5ec3")
        config:
            config

When ``--commit`` is combined with ``--branch`` or ``--tag``, the commit takes precedence both for checking out the repository locally during deployment and for the ref written into the generated ``Snakefile``.
``--commit`` can also be used on its own, without ``--branch`` or ``--tag``.

For more options and details, run

.. code-block:: console

    $ snakedeploy deploy-workflow --help

The same interaction can be done from within Python, see :ref:`api_reference_snakedeploy` for details.
