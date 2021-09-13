#!/bin/bash --login

set -eux

#---- setup runtime evironment
source $HOFX_HOMEDIR/hofx/cfg/setup

#---- setup variables based on scheduler
RUN_ENVIR=${RUN_ENVIR:-""}
if [[ "$RUN_ENVIR" != "rocoto" ]]; then
  export SLURM_ACCOUNT=$account
  export SALLOC_ACCOUNT=$SLURM_ACCOUNT
  export SBATCH_ACCOUNT=$SLURM_ACCOUNT
  export SLURM_QOS=debug
  nprocs=24
  export APRUN="srun -n ${nprocs} --ntasks-per-node=3 -t 30:00"
fi

#---- execute hofx
$HOFX_HOMEDIR/hofx/scripts/hofx.sh $HOFX_HOMEDIR/hofx/cfg/expdir $ROTDIR/hofx_tmp/$CDATE
rc=$?
exit $rc
