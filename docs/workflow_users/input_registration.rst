.. _input_registration:

===================
Register input data
===================

Snakedeploy can help with generating sample/unit sheets from files on the filesystem.
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