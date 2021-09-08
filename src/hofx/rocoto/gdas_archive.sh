#!/bin/bash --login

set -eux

export PYTHONPATH=$HOFX_HOMEDIR

$HOFX_HOMEDIR/hofx/scripts/archive.sh $HOFX_HOMEDIR/hofx/cfg/expdir $ROTDIR/hofx_tmp/$CDATE
rc=$?

# If requested, remove stage directory for current cycle 
KEEPDATA=$(echo ${KEEPDATA:-"NO"} | tr a-z A-Z)
if [[ $KEEPDATA = "NO" ]]; then
    string=`grep "cycle" $ROTDIR/hofx_tmp/$CDATE/archive.yaml | cut -d "'" -f2-2 | head -1`
    DATAROOT=$ROTDIR/${string}
    [[ -d $DATAROOT ]] && rm -rf $DATAROOT
fi

exit $rc
