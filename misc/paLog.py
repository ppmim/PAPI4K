#!/usr/bin/env python

# Copyright (c) 2009-2019 IAA-CSIC  - All rights reserved.
# Author: Jose M. Ibanez. 
# Instituto de Astrofisica de Andalucia, IAA-CSIC
#
# This file is part of PAPI (PANIC Pipeline)
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

"""
   Main routines for the loggin function.
"""
import logging
import datetime


class ColorFormatter(logging.Formatter):
 
    def color(self, level=None):
        codes = {
            None:       (0,   0),
            'DEBUG':    (0,  32),  # green
            'INFO':     (0,  33),  # yellow
            'WARNING':  (0,  34),  # blue
            'ERROR':    (1,  31),  # red
            'CRITICAL': (1, 101),  # blanco, fondo rojo
            'RESULT':   (0, 104)   # blanco, fondo cian
            }
        return (chr(27)+'[%d;%dm') % codes[level]
 
    def format(self, record):
        retval = logging.Formatter.format(self, record)
        return self.color(record.levelname) + retval + self.color()


# define the global variable used whole around the PAPI sources
log = logging.getLogger('PAPI')

if (log.hasHandlers()):
    log.handlers.clear()


# Add a custom level for result messages
RESULT_LEVEL_NUM = 60 
#logging.addLevelName(RESULT_LEVEL_NUM, "RESULT")
logging.addLevelName(RESULT_LEVEL_NUM, "RESULT")

def result(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(RESULT_LEVEL_NUM):
        self._log(RESULT_LEVEL_NUM, message, args, **kws) 

#logging.Logger.result = result
logging.Logger.result = result


# We define two logging handlers (Console and File), each one can have
# different properties (level, formater, ...)

### Console  ###
console = logging.StreamHandler()
console.setLevel(logging.DEBUG) # here we set the level for console handler
# NOTE: Handler.setLevel() method, just as in logger objects, specifies the
# lowest severity that will be dispatched to the appropriate destination.
# Why are there two setLevel() methods? The level set in the logger determines
# which severity of messages it will pass to its handlers. The level set in
# each handler determines which messages that handler will send on.
console.setFormatter(ColorFormatter('    [%(name)s]: %(asctime)s %(levelname)-8s %(module)s:%(lineno)d: %(message)s'))
log.addHandler(console)


### File ###
datetime_str = str(datetime.datetime.utcnow()).replace(" ","T")
file_hd = logging.FileHandler("/tmp/papi_" + datetime_str + ".log")
# If we need to know later the filaname given--> paLog.file_hd.baseFilename
file_hd.setLevel(logging.DEBUG)  # here we set the level for File handler
formatter = logging.Formatter('[%(name)s]: %(asctime)s %(levelname)-8s %(module)s:%(lineno)d: %(message)s')
file_hd.setFormatter(formatter)
#logging.getLogger('PAPI').addHandler(file_hd)
log.addHandler(file_hd)

# define the global log level
#logging.getLogger('PAPI').setLevel(logging.DEBUG)  # debug is the lowest level
log.setLevel(logging.DEBUG)  # debug is the lowest level
