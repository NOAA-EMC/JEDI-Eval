#!/bin/bash --login

set -eux

#---- setup runtime evironment
source $HOFX_HOMEDIR/hofx/cfg/setup
export PYTHONPATH=$PYTHONPATH:$EMCPY_HOMEDIR

#---- execute diags
$HOFX_HOMEDIR/hofx/scripts/diags.sh $HOFX_HOMEDIR/hofx/cfg/expdir $ROTDIR/hofx_tmp/$CDATE
rc=$?

#---- if requested, remove files in $ROTDIR/diags for current cycle
KEEPDATA=$(echo ${KEEPDATA:-"NO"} | tr a-z A-Z)
if [[ $KEEPDATA = "NO" ]]; then
    eval $(source_yaml $ROTDIR/hofx_tmp/$CDATE/diags.yaml plot "window begin")
    RMFILES=$ROTDIR/diags/*${window_begin}.nc4
    rm -rf $RMFILES
fi

exit $rc
