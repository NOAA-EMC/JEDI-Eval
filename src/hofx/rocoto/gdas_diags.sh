#!/bin/bash --login

set -eux

export PYTHONPATH=$HOFX_HOMEDIR:$EMCPY_HOMEDIR

$HOFX_HOMEDIR/hofx/scripts/diags.sh $HOFX_HOMEDIR/hofx/cfg/expdir $ROTDIR/hofx_tmp/$CDATE
rc=$?

# If requested, remove files in $ROTDIR/diags for current cycle
KEEPDATA=$(echo ${KEEPDATA:-"NO"} | tr a-z A-Z)
if [[ $KEEPDATA = "NO" ]]; then
    string=`grep "window begin" $ROTDIR/hofx_tmp/$CDATE/diags.yaml | cut -d "'" -f2-2 | head -1`
    RMFILES=$ROTDIR/diags/*${string}.nc4
    rm -rf $RMFILES
fi

exit $rc
