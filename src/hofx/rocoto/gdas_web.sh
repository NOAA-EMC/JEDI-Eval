#!/bin/bash --login

set -eux

#---- setup runtime evironment
source $HOFX_HOMEDIR/hofx/cfg/setup
export PYTHONPATH=$PYTHONPATH:$EMCPY_HOMEDIR

#---- execute website generation
$HOFX_HOMEDIR/hofx/scripts/web.sh $HOFX_HOMEDIR/hofx/cfg/expdir $ROTDIR/hofx_tmp/$CDATE
rc=$?

exit $rc
