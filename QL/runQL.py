#! /usr/bin/env python

# Copyright (c) 2010 Jose M. Ibanez. All rights reserved.
# Institute of Astrophysics of Andalusia, IAA-CSIC
#
# This file is part of PAPI QL (PANIC Quick Look)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

################################################################################
#
# runQL (run the QL for PANIC pipeline)
#
# runQL.py
#
# Last update 22/Jan/2020
#
################################################################################


    ####################################################################
    #                                                                  #
    #                   This is where it all starts.                   #
    #         The body of this program is at the end of this file      #
    #                                                                  #
    ####################################################################


import sys
import os.path
import argparse

# Log
from papi.misc.paLog import log

# PAPI packages
from PyQt5 import QtCore, QtWidgets, QtGui, uic

# If ~/iraf/focus_seq.txt exists, QL fails because it try to launch iraf.obsutil.starfocus() 
try:
    if os.path.exists(os.path.expanduser("~") + "/iraf/focus_seq.txt"):
        os.unlink(os.path.expanduser("~") + "/iraf/focus_seq.txt")
except Exception as e:
    log.warning("Cannot delete ~/iraf/focus_seq.txt")

import papi.QL.mainGUI as mainGUI
import papi.misc.config

################################################################################
# main
################################################################################


def main(arguments=None):
    
    if arguments is None:
        arguments = sys.argv[1:] # ignore argv[0], the script name
    
    # Get and check command-line options
    
    description = ("This module in the main application for the PANIC"
                   "Quick Look (PQL) data reduction system")

    parser = argparse.ArgumentParser(description=description)
    # general options
    
    parser.add_argument("-c", "--config", type=str,
                        action="store", dest="config_file",
                        help="config file for the PANIC Pipeline application. "
                           "If not specified, '%s' is used" \
                        % papi.misc.config.default_config_file())
    
    parser.add_argument("-v", "--verbose",
                  action="store_true", dest="verbose", default=True,
                  help="verbose mode [default]")
    
    parser.add_argument("-s", "--source", type=str,
                  action="store", dest="source",
                  help="Source directory of data frames. It has to be a fullpath file name")
    
    parser.add_argument("-o", "--output_dir", type=str,
                  action="store", dest="output_dir",
                        help="output directory to write products")
    
    parser.add_argument("-t", "--temp_dir", type=str,
                  action="store", dest="temp_dir",
                        help="temporary directory to write")

    init_options = parser.parse_args(args=arguments)
    
    # Read the default configuration file if none was specified by the user
    if not init_options.config_file:
        config_file = papi.misc.config.default_config_file()
    else:
        config_file = init_options.config_file
    
    # now, we "mix" the invokation parameter values with the values in the
    # config file having priority the invokation values over config file values
    # note: only values of the 'quicklook' section can be invoked
    options = papi.misc.config.read_options(init_options, 'quicklook', config_file)

    ql_opts = options['quicklook']
    
    if not ql_opts['source'] or not ql_opts['output_dir'] or not ql_opts['temp_dir']: 
        parser.print_help()
        parser.error("Incorrect number of arguments " )
    
    log.debug("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    log.debug(">> Starting Quick-Look....")
    log.debug("   + source  : %s", ql_opts['source'])
    log.debug("   + out_dir : %s", ql_opts['output_dir'])
    log.debug("   + temp_dir : %s", ql_opts['temp_dir'])
    log.debug("   + run_mode: %s", ql_opts['run_mode'])
    log.debug("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    
    app = QtWidgets.QApplication(sys.argv)
    try:
        f = mainGUI.MainGUI(ql_opts['source'], ql_opts['output_dir'], 
                            ql_opts['temp_dir'], config_opts=options)
        f.show()
        app.exec_()
    except:
        log.debug("Some error while running mainGUI")
        raise

######################################################################
if __name__ == "__main__":
    sys.exit(main())

