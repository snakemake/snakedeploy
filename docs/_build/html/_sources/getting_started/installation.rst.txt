.. _getting_started-installation:

============
Installation
============

Snakedeploy can be installed via pypi or from source.


Install from source
===================

.. code:: console

    $ git clone git@github.com:snakemake/snakedeploy.git
    $ cd snakedeploy
    $ pip install .


.. code:: console

    $ pip install -e .


Install via pip
===============

Snakedeploy can also be installed with pip.

.. code:: console

    $ pip install snakedeploy


Once it's installed, you should be able to inspect the client!


.. code:: console

    usage: snakedeploy [-h] [--version] [--quiet] [--template] [--name NAME] [--verbose] [--log-disable-color] [--log-use-threads] [--force]
                       [repo] [dest]

    Snakedeploy: deploy snakemake pipelines from version control.

    positional arguments:
      repo                 Repository address and destination to deploy, e.g., <source> <dest>
      dest                 Path to clone the repository, should not exist.

    optional arguments:
      -h, --help           show this help message and exit
          --version            print the version and exit.
      --quiet              suppress additional output.
      --force              If the folder exists, force overwrite, meaning remove and replace.

    DEPLOY:
      --template           Template the repository first (a disconnected fork) then clone. GITHUB_TOKEN is required.
      --name NAME          A custom name for your template repository, <org/username>/<repository>.

    LOGGING:
      --verbose            verbose output for logging.
      --log-disable-color  Disable color for snakedeploy logging.
      --log-use-threads    Force threads rather than processes.


Snakemake is available on PyPi as well as through Bioconda and also from source code.
You can use one of the following ways for installing Snakemake.
