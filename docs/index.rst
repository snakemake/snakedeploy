.. _manual-main:

============
Snakedeploy
============

.. image:: https://img.shields.io/pypi/pyversions/snakedeploy.svg
    :target: https://www.python.org

.. image:: https://img.shields.io/pypi/v/snakedeploy.svg
    :target: https://pypi.python.org/pypi/snakedeploy

.. image:: https://github.com/snakemake/snakedeploy/workflows/CI/badge.svg?branch=main&label=CI
    :target: https://github.com/snakemake/snakemake/actions?query=branch%3Amain+workflow%3ACI

.. image:: https://img.shields.io/discord/753690260830945390?label=discord%20chat   
    :alt: Discord
    :target: https://discord.gg/NUdMtmr

.. image:: https://img.shields.io/github/stars/snakemake/snakedeploy?style=social
    :alt: GitHub stars
    :target: https://github.com/snakemake/snakemake/stargazers


SnakeDeploy is a command line and interactive Python client
to easily deploy snakemake pipelines from version control like GitHub.
To learn more about Snakemake, visit the `official documentation <https://snakemake.readthedocs.io/>`_


.. _main-getting-started:

---------------
Getting started
---------------

Deployment means that you have the following options:

 1. Clone the repository template as is, removing the .git history
 2. "Template" the repository (meaning forking without keeping connected to the parent) and clone the fork. In this case, we keep the .git history as you will likely want to push back to the repository.

For the second option, you will need a `GITHUB_TOKEN` (a personal access token) exported in
the environment. You are also given the option to specify the `--name` of your templated repository.
Both of these options are discussed in :ref:`deploy`.

The library is fairly simple now, but will be used as a base for an interactive
tool to run snakemake workflows. Stay tuned!

.. _main-support:

-------
Support
-------

* In case of **questions**, please post on `stack overflow <https://stackoverflow.com/questions/tagged/snakemake>`_.
* To **discuss** with other Snakemake users, you can use the `mailing list <https://groups.google.com/forum/#!forum/snakemake>`_. **Please do not post questions there. Use stack overflow for questions.**
* For **bugs and feature requests**, please use the `issue tracker <https://github.com/snakemake/snakedeploy/issues>`_.
* For **contributions**, visit Snakemake on `Github <https://github.com/snakemake/snakedeploy>`_.

---------
Resources
---------

`Snakemake Repository <https://snakemake.readthedocs.org>`_
    The Snakemake workflow manager repository houses the core software for Snakemake.

`Snakemake Wrappers Repository <https://snakemake-wrappers.readthedocs.org>`_
    The Snakemake Wrapper Repository is a collection of reusable wrappers that allow to quickly use popular tools from Snakemake rules and workflows.

`Snakemake Workflows Project <https://github.com/snakemake-workflows/docs>`_
    This project provides a collection of high quality modularized and re-usable workflows.
    The provided code should also serve as a best-practices of how to build production ready workflows with Snakemake.
    Everybody is invited to contribute.

`Snakemake Profiles Project <https://github.com/snakemake-profiles/doc>`_
    This project provides Snakemake configuration profiles for various execution environments.
    Please consider contributing your own if it is still missing.

`Bioconda <https://bioconda.github.io/>`_
    Bioconda can be used from Snakemake for creating completely reproducible workflows by defining the used software versions and providing binaries.

.. toctree::
   :caption: Getting started
   :name: getting_started
   :hidden:
   :maxdepth: 1

   getting_started/installation

.. toctree::
  :caption: Deploy templates
  :name: deployTemplates
  :hidden:
  :maxdepth: 1

  deploy/deploy
  deploy/template

.. toctree::
    :caption: API Reference
    :name: api-reference
    :hidden:
    :maxdepth: 1

    api_reference/snakedeploy
    api_reference/internal/modules
