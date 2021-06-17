#!/bin/bash
# stage.sh
# stage hofx files
set -eux

#----- other variables
# REMOVE later
MYPATH=`readlink -f "$0"`
MYDIR=`dirname "$MYPATH"`
gitdir=$MYDIR/..
alias source_yaml=$gitdir/bin/source_yaml
alias create_bundle=$gitdir/bin/create_bundle
alias detect_host=$gitdir/bin/detect_host
shopt -s expand_aliases

script_dir=$gitdir # what should this variable be? coming from rocoto I assume, and not "$HOMEgfs"

#----- get machine and source runtime environment
set +x
machine=$(detect_host)
source $gitdir/cfg/platform/$machine/JEDI
set -x

#----- TEMPORARY
set +u
export PYTHONPATH=$PYTHONPATH:$gitdir/../
set -u
#----- END TEMPORARY

#----- export R2D2_CONFIG based off of $EXPDIR/r2d2.yaml
eval $(source_yaml $EXPDIR/r2d2.yaml r2d2 r2d2_config)
export R2D2_CONFIG=$r2d2_config

#----- stage FV3JEDI files (do this here or as part of experiment setup?)
python $script_dir/stage_fv3jedi.py $EXPDIR

#----- stage cycle dependent files
python $script_dir/stage_obs.py $EXPDIR
python $script_dir/stage_bkg.py $EXPDIR