#!/bin/bash --login

set -eux

export PYTHONPATH=$HOFX_HOMEDIR:$EMCPY_HOMEDIR

$HOFX_HOMEDIR/hofx/scripts/diags.sh $HOFX_HOMEDIR/hofx/cfg/expdir $ROTDIR/hofx_tmp/$CDATE
rc=$?

# If requested, remove files in $ROTDIR/diags for current cycle
KEEPDATA=$(echo ${KEEPDATA:-"NO"} | tr a-z A-Z)
if [[ $KEEPDATA = "NO" ]]; then
    alias source_yaml=$HOFX_HOMEDIR/hofx/bin/source_yaml
    shopt -s expand_aliases

    set +eux
    source $HOFX_HOMEDIR/hofx/cfg/platform/$machine/JEDI
    set -eux

    eval $(source_yaml $ROTDIR/hofx_tmp/$CDATE/diags.yaml plot "window begin")
    RMFILES=$ROTDIR/diags/*${window_begin}.nc4
    rm -rf $RMFILES
fi

exit $rc
