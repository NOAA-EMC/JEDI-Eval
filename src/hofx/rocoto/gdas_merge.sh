#!/bin/bash --login

set -eux

#---- setup runtime evironment
source $HOFX_HOMEDIR/hofx/cfg/setup

#---- execute merge
$HOFX_HOMEDIR/hofx/scripts/merge.sh $HOFX_HOMEDIR/hofx/cfg/expdir $ROTDIR/hofx_tmp/$CDATE
rc=$?
exit $rc
