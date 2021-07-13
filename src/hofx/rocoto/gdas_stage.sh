#!/bin/bash --login

set -eux

echo "PYTHONPATH= $PYTHONPATH"

$HOFX_HOMEDIR/hofx/test/stage_example.sh $HOFX_HOMEDIR/hofx/cfg/expdir $ROTDIR/hofx_tmp
rc=$?
echo $rc
