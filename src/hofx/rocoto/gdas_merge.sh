#!/bin/bash --login

set -eux

export PYTHONPATH=$HOFX_HOMEDIR

#---- other variables
alias source_yaml=$HOFX_HOMEDIR/hofx/bin/source_yaml
alias create_bundle=$HOFX_HOMEDIR/hofx/bin/create_bundle
alias detect_host=$HOFX_HOMEDIR/hofx/bin/detect_host
shopt -s expand_aliases

#---- get machine and setup runtime environment
set +eux
machine=${machine:-$(detect_host)}
source $HOFX_HOMEDIR/hofx/cfg/platform/$machine/JEDI
export R2D2_CONFIG=$HOFX_HOMEDIR/hofx/cfg/platform/$machine/r2d2_config.yaml
set -eux

#---- execute merge
$HOFX_HOMEDIR/hofx/scripts/merge.sh $HOFX_HOMEDIR/hofx/cfg/expdir $ROTDIR/hofx_tmp/$CDATE
rc=$?
exit $rc
