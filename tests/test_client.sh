#!/bin/bash

echo
echo "************** START: test_client.sh **********************"

# Create temporary testing directory
echo "Creating temporary directory to work in."
here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

. $here/helpers.sh

# Make sure it's installed
if which snakedeploy >/dev/null; then
    printf "snakedeploy is installed\n"
else
    printf "snakedeploy is not installed\n"
    exit 1
fi

# Create temporary testing directory
tmpdir=$(mktemp -d)
output=$(mktemp ${tmpdir:-/tmp}/snakedeploy_test.XXXXXX)
repo="https://github.com/snakemake-workflows/dna-seq-varlociraptor"
dest=$tmpdir/github-testing
printf "Created temporary directory to work in. ${output}\n"

echo
echo "#### Testing snakedeploy --help"
runTest 0 $output snakedeploy --help

echo
echo "#### Testing snakedeploy GitHub deployment"
runTest 0 $output snakedeploy deploy-workflow "${repo}" "${dest}" --tag v1.0.0 --name dna-seq

echo
echo "#### Testing snakedeploy workflow directory exists"
runTest 1 $output snakedeploy deploy-workflow "${repo}" "${dest}" --tag v1.0.0

echo
echo "#### Testing snakedeploy directory exists but enforcing"
runTest 0 $output snakedeploy deploy-workflow "${repo}" "${dest}" --tag v1.0.0 --force

echo
echo "#### Testing snakedeploy GitLab deployment"
dest=$tmpdir/gitlab-testing
repo="https://gitlab.com/nate-d-olson/snaketestworkflow"
runTest 0 $output snakedeploy deploy-workflow "${repo}" "${dest}" --name snake-test --branch master

echo
echo "#### Testing snakedeploy local deployment"
local=$tmpdir/rna-seq-star-deseq2
repo="https://github.com/snakemake-workflows/rna-seq-star-deseq2"
dest=${tmpdir}/use-workflow-as-module
git clone ${repo} ${local}
runTest 0 $output snakedeploy deploy-workflow "${local}" ${dest} --tag v1.2.0

echo
echo "#### Testing snakedeploy update-conda-envs"
cp tests/test-env.yaml $tmpdir
runTest 0 $output snakedeploy update-conda-envs --conda-frontend conda $tmpdir/test-env.yaml

echo
echo "#### Testing snakedeploy pin-conda-envs"
runTest 0 $output snakedeploy pin-conda-envs --conda-frontend conda $tmpdir/test-env.yaml

echo
echo "#### Testing snakedeploy update-snakemake-wrappers with given git ref"
cp tests/test-snakefile.smk $tmpdir
runTest 0 $output snakedeploy update-snakemake-wrappers --git-ref v1.4.0 $tmpdir/test-snakefile.smk

echo
echo "#### Testing snakedeploy update-snakemake-wrappers without git ref"
runTest 0 $output snakedeploy update-snakemake-wrappers $tmpdir/test-snakefile.smk


rm -rf ${tmpdir}
