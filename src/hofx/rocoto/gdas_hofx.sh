#!/bin/bash --login

set -ex

$HOFX_HOMEDIR/hofx/test/hofx_example.sh $HOFX_HOMEDIR/hofx/cfg/expdir $ROTDIR/hofx_tmp
rc=$?
echo $rc
