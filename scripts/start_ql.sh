#!/bin/bash

# CONDA environment
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/obs22/anaconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/obs22/anaconda3/etc/profile.d/conda.sh" ]; then
        . "/home/obs22/anaconda3/etc/profile.d/conda.sh"
    else
        export PATH="/home/obs22/anaconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

conda activate papi

# Launch QL

export QT_GRAPHICSSYSTEM=native
QL_DIR=$PAPI_HOME/QL

cd $QL_DIR
# pyuic5 panicQL.ui > panicQL.py
# pyrcc5 -o panicQL_resources_rc.py resources/panicQL_resources.qrc

python runQL.py  -c ../config_files/papi.cfg
