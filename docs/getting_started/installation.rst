.. _getting_started-installation:

============
Installation
============

Snakedeploy can be installed via pixi, conda, pypi or from source.

Install via pixi
================
For global installation (recommended), run

.. code:: console

    $ pixi global install snakedeploy

For local installation into an existing pixi workspace, run

.. code:: console

    $ pixi add snakedeploy

Install via mamba/conda
=======================

.. code:: console

    $ mamba install -c bioconda -c conda-forge snakedeploy

or

.. code:: console

    $ conda install -c bioconda -c conda-forge snakedeploy


Install via pip
===============

.. code:: console

    $ pip install snakedeploy


Install from source
===================

.. code:: console

    $ git clone git@github.com:snakemake/snakedeploy.git
    $ cd snakedeploy
    $ pip install .


.. code:: console

    $ pip install -e .


Testing the installation
========================

Once snakedeploy is installed, you should be able to inspect the client with

.. code:: console

    snakedeploy --help
