#!/bin/bash
# hofx.sh
# run hofx executable
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

#----- get machine and source runtime environment
set +x
machine=$(detect_host)
source $gitdir/cfg/platform/$machine/JEDI
set -x

#----- TEMPORARY
set +u
export PYTHONPATH=$PYTHONPATH:$gitdir/../
script_dir=../../../darth/hofx/ # temporary for testing
set -u
#----- END TEMPORARY

#----- get shell variables from config YAML
eval $(source_yaml $EXPDIR/base.yaml base experiment_dir)
eval $(source_yaml $EXPDIR/base.yaml jedi jedi_build_dir)
eval $(source_yaml $EXPDIR/resources.yaml hofx nprocs)

#----- create YAML for hofx executable
HOFXYAML=$experiment_dir/${CDATE}/hofx.yaml
python $script_dir/genyaml.py hofx $HOFXYAML

#----- run executable
HOFXEXE=$jedi_build_dir/bin/fv3jedi_hofx_nomodel.x
$APRUN $HOFXEXE $HOFXYAML
