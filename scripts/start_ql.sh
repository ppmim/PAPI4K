#!/bin/bash


export QT_GRAPHICSSYSTEM=native
QL_DIR=$PAPI_HOME/QL

cd $QL_DIR
# pyuic5 panicQL.ui > panicQL.py
# pyrcc5 -o panicQL_resources_rc.py resources/panicQL_resources.qrc

python runQL.py  -c ../config_files/papi.cfg