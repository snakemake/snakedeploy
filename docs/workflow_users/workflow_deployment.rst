.. _deploy:

===================
Deploying workflows
===================

Snakedeploy enables you to automatically deploy a workflow from a public git repository to your local machine, by using Snakemake's module system.
Via the command line, deployment works as follows:

.. code-block:: console

    $ snakedeploy deploy-workflow https://github.com/snakemake-workflows/dna-seq-varlociraptor /tmp/dest --tag v1.0.0


Snakedeploy will then generate a workflow definition ``/tmp/dest/workflow/Snakefile`` that declares the given workflow as a module.
For the example above, it will have the following content


.. code-block:: python

    configfile: "config/config.yaml"


    # declare https://github.com/snakemake-workflows/dna-seq-varlociraptor as a module
    module dna_seq:
        snakefile: 
            "https://github.com/snakemake-workflows/raw/v1.0.0/workflow/Snakefile"
        config:
            config


    # use all rules from https://github.com/snakemake-workflows/dna-seq-varlociraptor
    use rule * from dna_seq

In addition, it will copy over the contents of the ``config`` directory of the given repository into ``/tmp/dest/workflow/Snakefile``.
These should be seen as a template, can be modified according to your needs.
Further, the workflow definition Snakefile can be arbitrarily extended and modified, thereby making any changes to the used workflow transparent (also see the `snakemake module documentation <https://snakemake.readthedocs.io/en/stable/snakefiles/modularization.html#snakefiles-modules>`_).

It is highly advisable to put the deployed workflow into a new (perhaps private) git repository (e.g., see `here <https://docs.github.com/en/github/importing-your-projects-to-github/adding-an-existing-project-to-github-using-the-command-line>`_ for instructions how to do that with Github).

For more options and details, run

.. code-block:: console

    $ snakedeploy deploy-workflow --help

The same interaction can be done from within Python, see :ref:`api_reference_snakedeploy` for details.
