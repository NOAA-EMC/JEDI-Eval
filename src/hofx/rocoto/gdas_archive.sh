#!/bin/bash --login

set -eux

#---- setup runtime evironment
source $HOFX_HOMEDIR/hofx/cfg/setup

#---- execute archive
$HOFX_HOMEDIR/hofx/scripts/archive.sh $HOFX_HOMEDIR/hofx/cfg/expdir $ROTDIR/hofx_tmp/$CDATE
rc=$?

#---- if requested, remove stage directory for current cycle 
KEEPDATA=$(echo ${KEEPDATA:-"NO"} | tr a-z A-Z)
if [[ $KEEPDATA = "NO" ]]; then
    eval $(source_yaml ${ROTDIR}/hofx_tmp/${CDATE}/archive.yaml archive cycle )
    DATAROOT=$ROTDIR/${cycle}
    [[ -d $DATAROOT ]] && rm -rf $DATAROOT
fi

exit $rc
