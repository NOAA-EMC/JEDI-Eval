#!/bin/bash --login

set -eux

$HOFX_HOMEDIR/hofx/test/merge_example.sh $HOFX_HOMEDIR/hofx/cfg/expdir $ROTDIR/hofx_tmp
rc=$?
echo $rc
