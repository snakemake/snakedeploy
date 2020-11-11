# SnakeDeploy

[![PyPI version](https://badge.fury.io/py/snakedeploy.svg)](https://badge.fury.io/py/snakedeploy)

![https://raw.githubusercontent.com/snakemake/snakedeploy/main/img/snakedeploy.png](https://raw.githubusercontent.com/snakemake/snakedeploy/main/img/snakedeploy.png)

Deploy a snakemake pipeline from GitHub.

## Getting Started

SnakeDeploy is the start of a command line and interactive Python client
to easily deploy snakemake pipelines from version control like GitHub.

### 1. Install

You first might want to install the software. You can do this from GitHub or
from pypi.

```bash
pip install snakedeploy
```
or
```bash
git clone git@github.com:snakemake/snakedeploy.git
cd snakedeploy
pip install .
```

If you plan to develop and want to install from the local folder, you can do:

```bash
pip install -e .
```

You can then interact with the client.

```bash
$ snakedeploy --help
usage: snakedeploy [-h] [--version] [--verbose] [--log-disable-color] [--log-use-threads] [--force] repo dest {version} ...

Snakedeploy: deploy snakemake pipelines from version control.

positional arguments:
  repo                 Repository address and destination to deploy, e.g., <source> <dest>
  dest                 Path to clone the repository, should not exist.

optional arguments:
  -h, --help           show this help message and exit
  --version            suppress additional output.
  --verbose            verbose output for logging.
  --log-disable-color  Disable color for snakedeploy logging.
  --log-use-threads    Force threads rather than processes.
  --force              If the folder exists, force overwrite, meaning remove and replace.

actions:
  snakedeploy subparsers

  {version}            snakedeploy actions
    version            show software version
```

### 2. Deploy

#### Command Line

The simplest functionality is to deploy a pipeline, which basically means 
cloning a repository to a particular destination. You can do that as follows:

```bash
$ snakedeploy https://github.com/snakemake-workflows/dna-seq-varlociraptor /tmp/dest
```
You'll then see the repository clone

```bash
Cloning into '/tmp/dest'...
remote: Enumerating objects: 99, done.
remote: Counting objects: 100% (99/99), done.
remote: Compressing objects: 100% (71/71), done.
remote: Total 1762 (delta 52), reused 55 (delta 26), pack-reused 1663
Receiving objects: 100% (1762/1762), 19.44 MiB | 2.63 MiB/s, done.
Resolving deltas: 100% (1122/1122), done.
Repository snakemake-workflows/dna-seq-varlociraptor cloned to /tmp/dest. Edit config and sample sheets.
```

And inspect the files there!

```bash
$ ls /tmp/dest/
config  LICENSE  README.md  workflow
```

#### Python

These same interactions can be done from within Python.

```python
from snakedeploy.providers import ProviderRunner
provider = ProviderRunner()
dest = provider.deploy("https://github.com/snakemake-workflows/dna-seq-varlociraptor", "/tmp/dest")
```

The library is fairly simple now, but will be used as a base for an interactive
tool to run snakemake workflows. Stay tuned!

## License

 * Free software: MPL 2.0 License
