#!/bin/bash
# archive_example.sh
# example of archiving diags to R2D2 after merging

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
$gitdir/bin/genYAML archive $EXPDIR $WORKDIR/archive.yaml

#---- run archiveJEDI based on configuration
$gitdir/bin/archiveJEDI $WORKDIR/archive.yaml
