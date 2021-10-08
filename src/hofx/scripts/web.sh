#!/bin/bash
# web.sh
# script to generate HTML based on available plots

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

mkdir -p $WORKDIR
cd $WORKDIR

#---- run genYAML to create YAML file
export CDATE=${CDATE:-2020121500}
$gitdir/bin/genYAML web $EXPDIR $WORKDIR/web.yaml

#---- generate HTML for the experiment
$gitdir/bin/genWWW $WORKDIR/web.yaml
