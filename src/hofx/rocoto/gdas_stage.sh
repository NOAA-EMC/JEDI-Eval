#!/bin/bash --login

set -eux

#---- setup runtime evironment
source $HOFX_HOMEDIR/hofx/cfg/setup

#---- execute stage
$HOFX_HOMEDIR/hofx/scripts/stage.sh $HOFX_HOMEDIR/hofx/cfg/expdir $ROTDIR/hofx_tmp/$CDATE
rc=$?
exit $rc
