.. _deploy:

==================
Deploy from GitHub
==================

**Important** This is the suggested approach, as the template API will not work if
there are any files over 10MB.

Command Line
============

The simplest functionality is to deploy a pipeline, which basically means 
cloning a repository to a particular destination. Since we don't want to keep git
history and accidentally push to a template, the .git folder is removed.
You can do that as follows:

.. code-block:: console

    $ snakedeploy https://github.com/snakemake-workflows/dna-seq-varlociraptor /tmp/dest


You'll then see the repository clone

.. code-block:: console

    Cloning into '/tmp/dest'...
    remote: Enumerating objects: 99, done.
    remote: Counting objects: 100% (99/99), done.
    remote: Compressing objects: 100% (71/71), done.
    remote: Total 1762 (delta 52), reused 55 (delta 26), pack-reused 1663
    Receiving objects: 100% (1762/1762), 19.44 MiB | 2.63 MiB/s, done.
    Resolving deltas: 100% (1122/1122), done.
    Repository snakemake-workflows/dna-seq-varlociraptor cloned to /tmp/dest. Edit config and sample sheets.


And inspect the files there!


.. code-block:: console

    $ ls /tmp/dest/
    config  LICENSE  README.md  workflow


This method doesn't require any sort of GitHub credential, and doesn't create a remote
repository for you.

Python
======

These same interactions can be done from within Python.

.. code-block:: console

    $ from snakedeploy.providers import ProviderRunner
    $ provider = ProviderRunner()
    $ dest = provider.deploy("https://github.com/snakemake-workflows/dna-seq-varlociraptor", "/tmp/dest")

