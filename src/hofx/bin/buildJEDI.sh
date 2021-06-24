#!/bin/bash
# buildJEDI.sh
# Usage: buildJEDI.sh /path/to/user.yaml /path/to/repos.yaml
# This script will do the following:
# - setup build environment
# - source YAML files to get configuration
# - create clone/build directories
# - create CMakeLists.txt file for ecbuild
# - run ecbuild
# - run make update (if needed)
# - run make
# - submit/run ctests

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 /path/to/user.yaml /path/to/repos.yaml" >&2
  exit 1
fi
set -eux

#---- get command line arguments
USERYAML=$1
REPOYAML=$2

#---- other variables
# REMOVE later
MYPATH=`readlink -f "$0"`
MYDIR=`dirname "$MYPATH"`
gitdir=$MYDIR/..
alias source_yaml=$gitdir/bin/source_yaml
alias create_bundle=$gitdir/bin/create_bundle
alias detect_host=$gitdir/bin/detect_host
shopt -s expand_aliases

#---- get machine and setup build environment
set +eux
machine=$(detect_host)
source $gitdir/cfg/platform/$machine/JEDI
set -eux

#---- source needed shell variables from user YAML
eval $(source_yaml $USERYAML user account build_dir bundle_dir clean_build clean_bundle update_jedi test_jedi)

#---- setup variables based on scheduler
if [ $scheduler == "slurm" ]; then
  export SLURM_ACCOUNT=$account
  export SALLOC_ACCOUNT=$SLURM_ACCOUNT
  export SBATCH_ACCOUNT=$SLURM_ACCOUNT
  export SLURM_QOS=debug
fi

#---- setup clone/build directories
[[ ${clean_bundle:-} =~ [YyTt] ]] && rm -rf $bundle_dir
[[ ! -d $bundle_dir ]] && mkdir -p $bundle_dir

[[ ${clean_build:-} =~ [YyTt] ]] && rm -rf $build_dir
[[ ! -d $build_dir ]] && mkdir -p $build_dir

#----- TEMPORARY
set +u
export PYTHONPATH=$PYTHONPATH:$gitdir/../
set -u
#----- END TEMPORARY

#---- create ecbuild CMakeLists.txt file
create_bundle $REPOYAML $bundle_dir

#---- run ecbuild
cd $build_dir
$ecbuild_cmd $bundle_dir

#---- run make update
[[ ${update_jedi:-} =~ [YyTt] ]] && make update

#---- run make command
$make_cmd

#---- run the 'get' ctests that need to run on login node
ctest -R get_

#---- run other ctests if the option is set
[[ ${test_jedi:-} =~ [YyTt] ]] && ctest -E -R get_
exit $?
