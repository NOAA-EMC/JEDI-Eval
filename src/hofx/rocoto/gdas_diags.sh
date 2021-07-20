#!/bin/bash --login

set -eux

export PYTHONPATH=$HOFX_HOMEDIR

echo "$HOFX_HOMEDIR/hofx/scripts/diags.sh $HOFX_HOMEDIR/hofx/cfg/expdir $ROTDIR/hofx_tmp"
rc=$?
exit $rc
