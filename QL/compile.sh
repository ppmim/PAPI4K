#!/bin/bash

#/home/panic/SOFTWARE/PAPI/PyQt-x11-gpl-4.9.4/pyuic/pyuic4 panicQL.ui > panicQL.py

export QT_GRAPHICSSYSTEM=native

pyuic5 panicQL.ui > panicQL.py
pyrcc5 -o panicQL_resources_rc.py resources/panicQL_resources.qrc

python runQL.py  -c ../config_files/papi.cfg
