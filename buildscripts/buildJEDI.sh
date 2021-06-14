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
set -eux

#---- get command line arguments
USERYAML=$1
REPOYAML=$2
PLATFORMYAML=$3

#---- other variables
gitdir=$PWD/..
src_yaml=$gitdir/buildscripts/source_yaml
gen_bundle=$gitdir/buildscripts/create_bundle

#---- source needed shell variables
eval $($src_yaml $USERYAML user account build_dir bundle_dir clean_build clean_bundle update_jedi test_jedi)
eval $($src_yaml $PLATFORMYAML platform JEDIOPT metamodule make_cmd ecbuild_cmd)
echo $ecbuild_cmd
echo $bundle_dir

#---- load build environment
set +x
module use $JEDIOPT/modulefiles/core
module load $metamodule
set -x

#---- setup clone/build directories
if [ ! -d $bundle_dir ]; then
  mkdir -p $bundle_dir
else
  if [ $clean_bundle == "YES" ]; then
    rm -rf $bundle_dir
  fi
fi

if [ ! -d $build_dir ]; then
  mkdir -p $build_dir
else
  if [ $clean_build == "YES" ]; then
    rm -rf $build_dir
  fi
fi

#---- create ecbuild CMakeLists.txt file
$gen_bundle $REPOYAML $bundle_dir

#---- run ecbuild
cd $build_dir
$ecbuild_cmd $bundle_dir

#---- run make update
if [ $update_jedi == "YES" ]; then
  make update
fi

#---- run make command
$make_cmd

#---- run ctests
if [ $test_jedi == "YES" ]; then
  ctest
fi
