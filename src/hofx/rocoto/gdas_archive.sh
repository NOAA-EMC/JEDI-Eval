#!/bin/bash --login

set -eux

export PYTHONPATH=$HOFX_HOMEDIR

#---- other variables
alias source_yaml=$HOFX_HOMEDIR/hofx/bin/source_yaml
alias create_bundle=$HOFX_HOMEDIR/hofx/bin/create_bundle
alias detect_host=$HOFX_HOMEDIR/hofx/bin/detect_host
shopt -s expand_aliases

#---- get machine and setup runtime environment
set +eux
machine=${machine:-$(detect_host)}
source $HOFX_HOMEDIR/hofx/cfg/platform/$machine/JEDI
export R2D2_CONFIG=$HOFX_HOMEDIR/hofx/cfg/platform/$machine/r2d2_config.yaml
set -eux

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
