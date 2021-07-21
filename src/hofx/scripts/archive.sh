#!/bin/bash
# archive.sh
# archive diags to R2D2 after merging

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 /path/to/expdir /path/to/workdir" >&2
  exit 1
fi
set -eux

#---- get command line arguments
EXPDIR=$1
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

#---- get machine and setup runtime environment
set +eux
machine=${machine:-$(detect_host)}
source $gitdir/cfg/platform/$machine/JEDI
export R2D2_CONFIG=$gitdir/cfg/platform/$machine/r2d2_config.yaml
set -eux

mkdir -p $WORKDIR
cd $WORKDIR

#---- run genYAML to create YAML file
export CDATE=${CDATE:-2020121500}
$gitdir/bin/genYAML archive $EXPDIR $WORKDIR/archive.yaml

#---- run archiveJEDI based on configuration
$gitdir/bin/archiveJEDI $WORKDIR/archive.yaml
