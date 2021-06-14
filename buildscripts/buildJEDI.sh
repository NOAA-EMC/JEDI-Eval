#!/bin/bash
# buildJEDI.sh
# Usage: buildJEDI.sh /path/to/user.yaml /path/to/repos.yaml /path/to/platform.yaml
# This script will do the following:
# - source YAML files to get configuration
# - setup build environment
# - create clone/build directories
# - create CMakeLists.txt file for ecbuild
# - run ecbuild
# - run make update (if needed)
# - run make
# - submit/run ctests

# get command line arguments
USERYAML=$1
REPOYAML=$2
PLATFORMYAML=$3


