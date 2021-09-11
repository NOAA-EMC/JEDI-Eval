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

mkdir -p $WORKDIR
cd $WORKDIR

#---- run genYAML to create YAML file
export CDATE=${CDATE:-2020121500}
$gitdir/bin/genYAML hofx $USERYAML $WORKDIR/hofx.yaml

#---- run executable
eval $($gitdir/bin/source_yaml ${USERYAML}/experiment.yaml jedi_build)
${APRUN} $jedi_build/bin/fv3jedi_hofx_nomodel.x $WORKDIR/hofx.yaml

