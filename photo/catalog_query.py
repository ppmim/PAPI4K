#!/usr/bin/env python

# Copyright (c) 2009-2012 IAA-CSIC  - All rights reserved. 
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

"""Module to query on-line catalogs"""

################################################################################
#
#
# PAPI (PANIC PIpeline)
#
# mef.py
#
# Multi Extension FITS file basic operations
#
# Created    : 23/05/2011    jmiguel@iaa.es -
# Last update: 17/03/2014    jmiguel@iaa.es -
# TODO
#      - Migration to use Astroquery (http://www.astropy.org/astroquery/)
################################################################################

################################################################################
# Import necessary modules
import os
import urllib
import urllib.parse
import urllib.request
import urllib.error

# Logging
from papi.misc.paLog import log


class ICatalog (object):
    """ 
    Class to query on-line catalogs through Gator, the IRSA's 
    Catalog Search engine 
    """
    
    cat_names = {'2MASS':'fp_psc', 
                     'USNOB1': 'usno_b1',
                     'IRAS': 'iraspsc'
                     }
    outfmt = {'votable': 3,
              'ascii': 1
              }
    
    url = "http://irsa.ipac.caltech.edu/cgi-bin/Gator/nph-query"
    
    def __init__(self, *a, **k):
        """ The constructor """
        super (ICatalog, self).__init__ (*a, **k)
        
    
    def queryCatalog(self, ar, dec, sr=1, cat_name=None, 
                     out_filename=None, out_format='votable'):    
        """
        Query the catalog and return the output file format selected
        
        :param ra,dec: Right Ascension & Declination of center of conesearch
        :param sr: search radious (arcsecs)
        :param cat_name: catalog name where search will be done
        :param out_filename: filename where results will be saved;if absent, 
                the location will be a tempfile with a generated name
        :param out_format: format of the output generated; current options available are:
                - VO Table (XML) (votable) (default)
                - SVC (Software handshaking structure) message (svc)
                - ASCII table (ascii)
        :return: filename where results where saved (VOTABLE, ASCII_TABLE, ...)
        """
        
        params={}
        params['outfmt'] = ICatalog.outfmt[out_format]
        if float(dec)>0:
            params['objstr'] = str(ar) + " +" + str(dec) 
            # we must add a space between RA and Dec due to a recognized BUG 
            # in IRSA Gator Engine
        else:
            params['objstr'] = str(ar) + " " + str(dec)
            # we must add a space between RA and Dec due to a recognized BUG 
            # in IRSA Gator Engine 
        params['spatial'] = 'Cone'
        params['radius'] = sr
        params['catalog'] = cat_name
        
        log.debug("Searching into catalog: %s  RA: %s  Dec: %s  Radius(arcsec): %s"%(cat_name, ar, dec, sr))

        query = urllib.parse.urlencode(params)
        get_url = ICatalog.url + "?" + query

        #query = self.url + "?" + out_fmt + "&" +  radius + "&" + objstr + "&" \
        #        + spatial + "&" + catalog 
        
        log.debug("Query: %s", get_url)        

        # check if file exist
        if os.path.exists(out_filename):
            log.debug("Warning, overwriting file %s" %out_filename)
        
        try:
            urllib.request.urlcleanup()
            r = urllib.request.urlretrieve(get_url, out_filename)
        except urllib.error.ContentTooShortError as e:
            log.error("Amount of data available was less than the expected \
            amount; might download was interrupted : %s", e)
            raise e
        else:
            return r
        

################################################################################
# main
################################################################################
if __name__ == "__main__":
    log.debug( 'Testing ICatalog')
    
    icat = ICatalog ()
    res_file = None

    try:
        res_file = icat.queryCatalog(243.298750, +54.600278, 500, 
                                     ICatalog.cat_names['2MASS'], 
                                     "/tmp/prueba.xml", 
                                     'votable')[0]
        log.debug("Output file generated : %s", res_file) 
    except Exception as e:
        log.error("Sorry, cann't solve the query")
        raise e

