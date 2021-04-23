.. _getting_started-tools:

=====
Tools
=====

Snakedeploy provides several command line tools for preparing or otherwise
interacting with your data or workflow.


.. _deploy:

Deploying workflows
===================

Snakedeploy enables you to automatically deploy a workflow from a public git repository to your local machine, by using Snakemake's module system.

Command Line
------------

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
            "https://github.com/snakemake-workflows/workflow/Snakefile"
        config:
            config


    # use all rules from https://github.com/snakemake-workflows/dna-seq-varlociraptor
    use rule * from dna_seq

In addition, it will copy over the contents of the ``config`` directory of the given repository into ``/tmp/dest/workflow/Snakefile``.
These should be seen as a template, can be modified according to your needs.
Further, the workflow definition Snakefile can be arbitrarily extended and modified, thereby making any changes to the used workflow transparent (also see the `snakemake module documentation <https://snakemake.readthedocs.io/en/stable/snakefiles/modularization.html#snakefiles-modules>`_).

It is highly advisable to put the deployed workflow into a new (perhaps private) git repository (e.g., see `here <https://docs.github.com/en/github/importing-your-projects-to-github/adding-an-existing-project-to-github-using-the-command-line>`_ for instructions how to do that with Github).

Python
------

These same interactions can be done from within Python.

.. code-block:: console

    $ from snakedeploy.deploy import deploy
    $ deploy("https://github.com/snakemake-workflows/dna-seq-varlociraptor", dest_path="/tmp/dest", name="dna_seq", tag="v1.0.0", force=True)


Also see :ref:`api_reference_snakedeploy` for details.

Collecting Files
================

In addition to deploying workflows, snakedeploy helps with generating sample/unit sheets from files on the filesystem.
These can then be used to configure a Snakemake workflow.
Let's say that we have a tab separated sheet of inputs called ``unit-patterns.tsv``:

.. code:: console

    S743_Nr(?P<nr>[0-9]+)	S743_1/01_fastq/S743Nr{nr}.*.fastq.gz
    S839_Nr(?P<nr>[0-9]+)	S839_*/01_fastq/S839Nr{nr}.*.fastq.gz
    S888_Nr(?P<nr>[0-9]+)	S888/S888_1/01_fastq/S888Nr{nr}.*.fastq.gz


And then a file of samples, ``samples.tsv`` where the first column contains the sample ids. If we want to collect files on the system based on a glob
pattern of interest and print them to STDOUT (along with the sample id) we can do:

.. code:: console

    cut -f1 samples.tsv | tail -n+2 | snakedeploy collect-files --config unit-patterns.tsv


More specifically, the config sheet above lets us select, for each sample, a glob pattern, which is then used to obtain the files on disk that correspond to this sample, which are then printed tab separated to STDOUT, along with the sample id that we put in.
This allows us to obtain the path to the raw data of the given samples.