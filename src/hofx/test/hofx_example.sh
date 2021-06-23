#!/bin/bash
# hofx_example.sh
# example of running hofx executable

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 /path/to/expdir /path/to/workdir" >&2
  exit 1
fi
set -eux

#---- get command line arguments
USERYAML=$1
WORKDIR=$2

#---- other variables
# REMOVE later
MYPATH=`readlink -f "$0"`
MYDIR=`dirname "$MYPATH"`
gitdir=$MYDIR/..
alias source_yaml=$gitdir/bin/source_yaml
alias create_bundle=$gitdir/bin/create_bundle
alias detect_host=$gitdir/bin/detect_host
shopt -s expand_aliases

#---- get machine and setup build environment
set +eux
machine=$(detect_host)
source $gitdir/cfg/platform/$machine/JEDI
set -eux
eval $(source_yaml ${USERYAML}/base.yaml account)

#---- setup variables based on scheduler
if [ $scheduler == "slurm" ]; then
  export SLURM_ACCOUNT=$account
  export SALLOC_ACCOUNT=$SLURM_ACCOUNT
  export SBATCH_ACCOUNT=$SLURM_ACCOUNT
  export SLURM_QOS=debug
fi

mkdir -p $WORKDIR
cd $WORKDIR

#---- run genYAML to create YAML file
$gitdir/bin/genYAML hofx $USERYAML $WORKDIR/hofx.yaml

#---- run executable
eval $(source_yaml ${USERYAML}/base.yaml jedi_build)
# NOT finished do manually!
nprocs=6 # this will be in YAML eventually
${APRUN}${nprocs} -t 30:00 $jedi_build/bin/fv3jedi_hofx_nomodel.x $WORKDIR/hofx.yaml

