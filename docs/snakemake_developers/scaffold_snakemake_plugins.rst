.. _scaffold_snakemake_plugins:

==========================
Scaffold Snakemake Plugins
==========================

Snakedeploy can be used to scaffold the code needed to write Snakemake plugins.
This is done by executing

.. code:: console

    $ snakedeploy scaffold-snakemake-plugin <plugin_type>

where ``<plugin_type>`` is one of the following:

* ``executor`` - to scaffold a Snakemake executor plugin,
* ``storage`` - to scaffold a Snakemake storage plugin,
* ``report`` - to scaffold a Snakemake report plugin,
* ``scheduler`` - to scaffold a Snakemake scheduler plugin.

Snakedeploy will create a `pixi <https://pixi.sh>`__ project with state-of-the-art skeleton code for the requested plugin type, including all required class implementations, test cases and even github actions for continous testing.

For details and additional options, run

.. code:: console

    $ snakedeploy scaffold-snakemake-plugin --help