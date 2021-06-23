#!/bin/bash
# hofx_example.sh
# example of running hofx executable

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 /path/to/expdir /path/to/workdir" >&2
  exit 1
fi
set -eux

#---- get command line arguments
USERYAML=$1
WORKDIR=$2

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

mkdir -p $WORKDIR
cd $WORKDIR

#---- run genYAML to create YAML file
$gitdir/bin/genYAML hofx $USERYAML $WORKDIR/hofx.yaml

#---- run executable
eval $(source_yaml ${USERYAML}/base.yaml jedi_build)
# NOT finished do manually!
$APRUN $jedi_build/fv3jedi_hofx_nomodel.x $WORKDIR/hofx.yaml

