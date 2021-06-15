#!/bin/bash
# stage.sh
# stage hofx files
set -eux

#---- other variables
# REMOVE later
MYPATH=`readlink -f "$0"`
MYDIR=`dirname "$MYPATH"`
gitdir=$MYDIR/..
alias source_yaml=$gitdir/bin/source_yaml
alias create_bundle=$gitdir/bin/create_bundle
shopt -s expand_aliases

script_dir=$gitdir # what should this variable be? coming from rocoto I assume, and not "$HOMEgfs"

#---- get machine and source runtime environment
set +x
machine='hera' # placeholder
source $gitdir/cfg/platform/$machine/buildJEDI # change to stage later? or is one env sufficient?
set -x

# stage FV3JEDI files (do this here or as part of experiment setup?)
python $script_dir/stage_fv3jedi.py $EXPDIR

# here we need to either set environment variables for stage_*.py or create a YAML file to put in EXPDIR
# currently there is cycle.yaml and dates are defined but they can also use env vars
# TODO

# stage cycle dependent files
python $script_dir/stage_obs.py $EXPDIR
python $script_dir/stage_bkg.py $EXPDIR
