#!/bin/bash
# arch_diag.sh
# save diagnostics to R2D2
set -eux

#----- other variables
# REMOVE later
MYPATH=`readlink -f "$0"`
MYDIR=`dirname "$MYPATH"`
gitdir=$MYDIR/..
alias source_yaml=$gitdir/bin/source_yaml
alias create_bundle=$gitdir/bin/create_bundle
alias detect_host=$gitdir/bin/detect_host
shopt -s expand_aliases

#----- get machine and source runtime environment
set +x
machine=$(detect_host)
source $gitdir/cfg/platform/$machine/JEDI
set -x

#----- TEMPORARY
set +u
export PYTHONPATH=$PYTHONPATH:$gitdir/../
script_dir=../../../darth/hofx/ # temporary for testing
set -u
#----- END TEMPORARY

exit 0 # nothing for now
