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
echo "#### Testing snakedeploy deployment"
runTest 0 $output snakedeploy deploy-workflow "${repo}" "${dest}" --tag v1.0.0 --name dna-seq

echo
echo "#### Testing snakedeploy directory exists"
runTest 1 $output snakedeploy deploy-workflow "${repo}" "${dest}" --tag v1.0.0

echo
echo "#### Testing snakedeploy directory exists but enforcing"
runTest 0 $output snakedeploy deploy-workflow "${repo}" "${dest}" --tag v1.0.0 --force

echo
echo "#### Testing snakedeply update-conda-envs"
cp tests/test-env.yaml $output
runTest 0 $output snakedeploy update-conda-envs --conda-frontend conda $output/test-env.yaml

echo
echo "#### Testing snakedeply pin-conda-envs"
runTest 0 $output snakedeploy pin-conda-envs --conda-frontend conda $output/test-env.yaml

rm -rf ${tmpdir}
