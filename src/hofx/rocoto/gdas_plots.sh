#!/bin/bash --login

set -eux

export PYTHONPATH=$HOFX_HOMEDIR

$HOFX_HOMEDIR/hofx/scripts/plots.sh $HOFX_HOMEDIR/hofx/cfg/expdir $ROTDIR/hofx_tmp
rc=$?
exit $rc
