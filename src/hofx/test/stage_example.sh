#!/bin/bash
# stage_example.sh
# example of staging files for hofx

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
$gitdir/bin/genYAML stage $USERYAML $WORKDIR/stage.yaml

#---- run stageJEDI based on configuration
$gitdir/bin/stageJEDI $WORKDIR/stage.yaml