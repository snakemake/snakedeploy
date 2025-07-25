.. _scaffold_snakemake_plugins:

==========================
Scaffold Snakemake Plugins
==========================

Snakedeploy can be used to scaffold the code needed to write Snakemake plugins.
It utilizes `pixi <https://pixi.sh>`__ for this purpose, hence you need to have it installed first.
Assuming you want to create a new Snakemake ``executor`` plugin with the name ``something``.
First, create a corresponding pixi project with

.. code:: console

    $ pixi init --format pyproject snakemake-executor-plugin-something

thereby following the mandatory naming convention for Snakemake plugins, i.e. ``snakemake-<plugin_type>-plugin-<name>``.
Enter the created directory with

.. code:: console

    $ cd snakemake-executor-plugin-something

Then, you can scaffold the plugin code with Snakedeploy via

.. code:: console

    $ snakedeploy scaffold-snakemake-plugin executor

instead of ``executor``, any of the following is possible:

* ``executor`` - to scaffold a Snakemake executor plugin,
* ``storage`` - to scaffold a Snakemake storage plugin,
* ``report`` - to scaffold a Snakemake report plugin,
* ``scheduler`` - to scaffold a Snakemake scheduler plugin.

Snakedeploy will create a `pixi <https://pixi.sh>`__ project with state-of-the-art skeleton code for the requested plugin type, including all required class implementations, test cases and even github actions for continous testing.

For details and additional options, run

.. code:: console

    $ snakedeploy scaffold-snakemake-plugin --help