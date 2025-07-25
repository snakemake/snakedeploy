.. _manual-main:

============
Snakedeploy
============

.. image:: https://img.shields.io/conda/dn/bioconda/snakedeploy.svg?label=Bioconda&color=%23064e3b
    :target: https://bioconda.github.io/recipes/snakedeploy/README.html

.. image:: https://img.shields.io/pypi/pyversions/snakedeploy.svg?color=%23065f46
    :target: https://www.python.org

.. image:: https://img.shields.io/pypi/v/snakedeploy.svg?color=%23047857
    :target: https://pypi.python.org/pypi/snakedeploy

.. image:: https://img.shields.io/github/actions/workflow/status/snakemake/snakedeploy/main.yml?label=tests&color=%2310b981
    :target: https://github.com/snakemake/snakedeploy/actions?query=branch%3Amain+workflow%3ACI

.. image:: https://img.shields.io/badge/stack-overflow-orange.svg?color=%2334d399
    :target: https://stackoverflow.com/questions/tagged/snakemake

.. image:: https://img.shields.io/discord/753690260830945390?label=discord%20chat&color=%23a7f3d0
    :alt: Discord
    :target: https://discord.gg/NUdMtmr

.. image:: https://img.shields.io/badge/bluesky-follow-%23d1fae5
   :alt: Bluesky
   :target: https://bsky.app/profile/johanneskoester.bsky.social

.. image:: https://img.shields.io/badge/mastodon-follow-%23ecfdf5
   :alt: Mastodon
   :target: https://fosstodon.org/@johanneskoester



Snakedeploy is a command line tool and Python library for automation of deployment and maintenance tasks around `Snakemake and Snakemake workflows <https://snakemake.github.io>`.

* **Workflow users** can apply it to automatically :ref:`deploy (i.e. set up for use) <deploy>` public workflows for execution from machine or use it to :ref:`register input data <input_registration>` for their workflow configuration.
* **Workflow developers** can use it to automatically :ref:`update conda environment files <update_conda_envs>` or :ref:`Snakemake wrapper versions <update_snakemake_wrappers>` and :ref:`pin/lock conda environments<pin_conda_envs>` in their workflows.
* **Snakemake developers** can use it to :ref:`scaffold Snakemake plugins <scaffold_snakemake_plugins>` (i.e. to obtain a skeleton codebase as a starting point for each type of possible Snakemake plugin).

.. _main-support:

-------
Support
-------

* In case of **questions**, please post on `stack overflow <https://stackoverflow.com/questions/tagged/snakemake>`__ or ask on `Discord <https://discord.gg/NUdMtmr>`_.
* For **bugs and feature requests**, please use the `issue tracker <https://github.com/snakemake/snakedeploy/issues>`__.
* For **contributions**, visit snakedeploy on `Github <https://github.com/snakemake/snakedeploy>`__.

.. toctree::
   :caption: Getting started
   :name: getting_started
   :hidden:
   :maxdepth: 1

   getting_started/installation

.. toctree::
   :caption: Workflow users
   :name: workflow_users
   :hidden:
   :maxdepth: 1

   workflow_users/workflow_deployment
   workflow_users/input_registration

.. toctree::
   :caption: Workflow developers
   :name: workflow_developers
   :hidden:
   :maxdepth: 1

   workflow_developers/update_conda_envs
   workflow_developers/update_snakemake_wrappers

.. toctree::
   :caption: Snakemake developers
   :name: snakemake_developers
   :hidden:
   :maxdepth: 1

   snakemake_developers/scaffold_snakemake_plugins

.. toctree::
    :caption: API Reference
    :name: api-reference
    :hidden:
    :maxdepth: 1

    api_reference/snakedeploy
    api_reference/internal/modules
