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
eval $(source_yaml $HOFX_HOMEDIR/hofx/cfg/expdir/experiment.yaml account)

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
