#!/usr/bin/env python

# Copyright (c) 2009-2015 IAA-CSIC  - All rights reserved. 
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

################################################################################
# PAPI (PANIC PIpeline)
#
# calSuperFlat.py
#
# Compute a super sky flat using the dither frames (IRAF implementation)
#
# Created    : 13/03/2009    jmiguel@iaa.es -
# Last update: 15/04/2009    jmiguel@iaa.es - Created function and modified to accept command line arguments
#              03/03/2010    jmiguel@iaa.es - Big modification to convert to a class and make more checkings
#              16/09/2010    jmiguel@iaa.es - Renamed to calSuperFlat and added support to MEF files
#              23/09/2010    jmiguel@iaa.es - Added (optional) gain map creation and/or normaliced flat field
#              21/10/2010    jmiguel@iaa.es - Removed gain map computation
#              21/04/2015    jmiguel@iaa.es - Several improvemets and fixes.
#
# TODO
#    - dark subtraction
#    - bpm masking
################################################################################

################################################################################
# Import necessary modules

import sys
import os
import fileinput
import shutil
import argparse
import time

# PAPI
from papi.misc.paLog import log
from papi.misc.fileUtils import removefiles
from papi.misc.utils import clock, listToFile
from papi.datahandler.clfits import ClFits, isaFITS, checkDataProperties
from papi.misc.collapse import collapse
import papi.misc.robust as robust
from papi.misc.version import __version__

# Interact with FITS files
import astropy.io.fits as fits

# Pyraf modules
from pyraf import iraf
from iraf import noao
from iraf import mscred


class SuperSkyFlat(object):
    """
    Class used to build a super sky Flat from a dither set of science 
    frames containing objects.
    
    Parameters
    ----------
    
    file_list: list
        A list FITS files or directory
    output_filename: str
        File where log will be written
    
    Returns
    -------
        If no error return 0
    """
    def __init__(self,  filelist,  output_filename="/tmp/superFlat.fits",  
                 bpm=None, norm=True, temp_dir="/tmp/", median_smooth=False,
                 norm_value="median", check=False):
        """
        Initialization method.
        
        Parameters
        ----------
        
        filelist : list 
            It can be a file or a python-list having the list of files to use 
            for the super-flat.
            
        output_filename (optional): string
            Filename for the super flat created
            
        bpm (optional) : string 
            Bad pixel map to be used -- NOT YET IMPLEMENTED
            
        norm (optional): bool
            Flag to indicate if the super flat must be normalized
            
        median_smooth: bool
            If true, median smooth filter is applied to the combined Flat-Field

        norm_value: str
            statistics value to use for normalization (median|robust_mean);
            Default = median

        """

        self.start_time = time.time()

        # list of sources files to be used in sky-flat computation
        if isinstance(filelist, list):
            self.filelist = filelist
        elif os.path.isfile(filelist):
            self.filelist = [line.replace("\n", "") for line in fileinput.input(filelist)]
        else:
            raise Exception("Cannot read source files")
           
        # Trick to get the parent directory even when relative path is given
        self.temp_dir = os.path.abspath(os.path.join(output_filename, os.pardir)) 
        self.output_filename = output_filename  # full filename (path+filename)
        self.bpm = bpm
        self.norm = norm  # if true, the flat field will be normalized
        self.norm_value = norm_value
        self.__median_smooth = median_smooth
        self.check = check

    def create(self):
        """
        Create the super sky flat using sigma-clipping algorithm (and supporting MEF)
        """
        
        # del old files   
        log.debug("Start createSuperSkyFlat")
        if os.path.exists(self.output_filename): 
            os.remove(self.output_filename)
        
        # Check data integrity (all have the same properties)
        m_filelist = self.filelist
        if self.check and not checkDataProperties(m_filelist, c_ncoadds=False):
            log.error("Data integrity ERROR, some files not having same properties (FILTER, EXPTIME, NCOADDS or READMODE)")
            raise Exception("Found a data integrity error")
        
  
        tmp1 = (self.temp_dir + "/tmp_sf.fits").replace('//','/')
        removefiles(tmp1)
        log.info("Combining images...(images are scaled to have the same median)")
        listToFile(m_filelist, self.temp_dir + "/files.txt")
        # Combine the images to find out the super Flat using sigma-clip algorithm;
        # the input images are scaled to have the same median, the pixels containing 
        # objects are rejected by an algorithm based on the measured noise (sigclip),
        # and the flat-field is obtained by a median.
        print("Time taken: %s\n" %(time.time()-self.start_time))
        iraf.mscred.combine(input=("'" + "@" + self.temp_dir + "/files.txt" + "'").replace('//','/'),
                    output=tmp1,
                    combine='median',
                    ccdtype='',
                    offset='none',
                    reject='sigclip',
                    lsigma=3.0,
                    hsigma=3.0,
                    scale='median',
                    zero='none',
                    statsec='' #'[350:130,480:220]' # default, entire image or [*,*]
                    #masktype='none'
                    #scale='exposure',
                    #expname='EXPTIME'
                    #ParList = _getparlistname ('flatcombine')
                )
        print("Time taken: %s"%(time.time() - self.start_time))
        # Remove tmp file
        os.unlink(self.temp_dir + "/files.txt")
        
        #Median smooth the superFlat
        ## Median smooth the master (normalized) flat
        if self.__median_smooth:
            log.debug("Doing Median smooth of FF ...")
            iraf.mscmedian(
                    input=tmp1,
                    output=tmp1.replace(".fits","_smooth.fits"),
                    xwindow=20,
                    ywindow=20,
                    outtype="median"
                    )
            shutil.move(tmp1.replace(".fits","_smooth.fits"), tmp1)
            
            # Or using scipy ( a bit slower then iraf...)
            #from scipy import ndimage
            #filtered = ndimage.gaussian_filter(f[0].data, 20)


        
        # (optional) Normalize wrt chip 1
        # Note: the robust estimator used for normalizing the flat-flied is
        # median, however we can use also robust.mean() that produces a similar
        # result. 
        if self.norm:
            f = fits.open(tmp1, 'update', ignore_missing_end=True )
            # MEF frame
            if len(f) > 1:
                # normalize wrt to mode of chip 1 (SG1_1 or Q1)
                if 'INSTRUME' in f[0].header:
                    f_instrument = f[0].header['INSTRUME'].lower()
                else:
                    f_instrument = 'unknown'
                if f_instrument == 'panic': 
                    ext_name = 'SG1_1'
                    try:
                        f[ext_name].header
                    except KeyError:
                        ext_name = 'Q1'
                elif f_instrument == 'hawki': 
                    ext_name = 'CHIP2.INT1'
                else:
                    ext_name = 1
                    
                naxis1 = f[1].header['NAXIS1']
                naxis2 = f[1].header['NAXIS2']
                offset1 = int(naxis1 * 0.1)
                offset2 = int(naxis2 * 0.1)
                median = robust.r_nanmedian(f[ext_name].data[offset1 : naxis1 - offset1,
                                                    offset2 : naxis2 - offset2])
                mean = robust.r_nanmean(f[ext_name].data[offset1 : naxis1 - offset1, 
                                                  offset2 : naxis2 - offset2])
            
                mode = 3 * median - 2 * mean
                rob_mean = robust.r_nanmean(f[ext_name].data[offset1 : naxis1 - offset1, 
                                                  offset2 : naxis2 - offset2])
                log.debug("MEDIAN = %f" % median)
                log.debug("MEAN = %f" % mean)
                log.debug("ROB_MEAN = %f" % rob_mean)
                log.debug("MODE (estimated) = %f" % mode)
                
                # Select the robust estimator for normalization 
                if self.norm_value == "median":
                    norm_value = median
                else: 
                    norm_value = rob_mean
                msg = "Normalization of MEF master flat frame wrt chip 1. (value=%f)"%norm_value

                # Do the normalization wrt chip 1
                for i_ext in range(1, len(f)):
                    f[i_ext].data = robust.r_divisionN(f[i_ext].data, norm_value)
                    norm_mean = robust.r_nanmean(f[i_ext].data)
                    if norm_mean < 0.5 or norm_mean > 1.5:
                        log.warning("Suspicious normalized SuperFlat obtained. Mean value =%f" % norm_mean)
                
            # PANIC multi-chip full frame
            elif ('INSTRUME' in f[0].header and f[0].header['INSTRUME'].lower() == 'panic'
                  and f[0].header['NAXIS1'] == 4096 and f[0].header['NAXIS2'] == 4096
                  and not 'H4RG' in f[0].header['CAMERA']):
                # It supposed to have a full frame of old PANIC (h2rg) in one single
                # extension (GEIRS default).
                # Note that in Numpy, arrays are indexed as rows X columns (y, x),
                # contrary to FITS standard (NAXIS1=columns, NAXIS2=rows).
                #
                median = robust.r_nanmedian(f[0].data[200: 2048-200, 2048+200: 4096-200])
                #
                mean = robust.r_nanmean(f[0].data[200: 2048-200, 2048+200: 4096-200])
                #
                rob_mean = robust.r_nanmean(f[0].data[200: 2048-200, 2048+200: 4096-200])

                mode = 3 * median - 2 * mean
                log.debug("MEDIAN = %s" % median)
                log.debug("MEAN = %s" % mean)
                log.debug("ROB_MEAN = %s" % rob_mean)
                log.debug("MODE (estimated) = %s" % mode)
                # Select the robust estimator for normalization 
                if self.norm_value == "median":
                    norm_value = median
                else: 
                    norm_value = rob_mean
                msg = "Normalization of (full) PANIC master flat frame wrt chip 1. (value = %d)" % norm_value
                
                #f[0].data = f[0].data / rob_mean
                f[0].data = robust.r_division(f[0].data, norm_value)
                norm_mean = robust.r_nanmean(f[0].data)
                if norm_mean < 0.5 or norm_mean > 1.5:
                    log.warning("Suspicious normalized SuperFlat obtained. Mean value =%f" % norm_mean)
                    
            # PANIC-H4RG, or single detector H2RG PANIC frame (2k x 2k),
            # or O2000 frame
            else:
                naxis1 = f[0].header['NAXIS1']
                naxis2 = f[0].header['NAXIS2']
                offset1 = int(naxis1 * 0.1)
                offset2 = int(naxis2 * 0.1)
                median = robust.r_nanmedian(f[0].data[offset1: naxis1 - offset1,
                                                    offset2: naxis2 - offset2])
                mean = robust.r_nanmean(f[0].data[offset1: naxis1 - offset1,
                                                  offset2: naxis2 - offset2])
                rob_mean = robust.r_nanmean(f[0].data[offset1: naxis1 - offset1,
                                                  offset2: naxis2 - offset2])
                mode = 3 * median - 2 * mean
                log.debug("MEDIAN = %f" % median)
                log.debug("MEAN = %f" % mean)
                log.debug("MEAN_ROB = %f" % rob_mean)
                log.debug("MODE (estimated) = %f" % mode)
                
                # Select the robust estimator for normalization 
                if self.norm_value == "median":
                    norm_value = median
                else: 
                    norm_value = rob_mean
                msg = "Normalization of master (PANIC single detector frame or O2k) flat frame by value = %d)" % norm_value
                
                f[0].data = robust.r_division(f[0].data, norm_value)
                norm_mean = robust.r_nanmean(f[0].data)
                log.debug("NORM_MEAN = %f" % norm_mean)
                if norm_mean < 0.5 or norm_mean > 1.5:
                    log.warning("Suspicious normalized SuperFlat obtained. Mean value = %f" % norm_mean)
                    
            log.debug(msg)

            
            # Update FITS header 
            f[0].header.add_history("[calSuperFlat] Normalized Super-Flat created from : %s"%str(m_filelist))
            f[0].header.add_history(msg)
        else:
            # Update FITS header 
            f = fits.open(tmp1,'update', ignore_missing_end=True)
            f[0].header.add_history("[calSuperFlat] Non-Normalized Super-Flat created from : %s"%str(m_filelist))

        f[0].header.set('PAPITYPE','MASTER_SKY_FLAT','TYPE of PANIC Pipeline generated file')
        f[0].header.set('PAPIVERS', __version__, "PANIC Pipeline version")
        #
        if 'PAT_NEXP' in f[0].header:
            f[0].header.set('PAT_NEXP', 1, 'Number of Positions into the dither pattern')

        f[0].header.set('IMAGETYP','MASTER_SKY_FLAT','TYPE of PANIC Pipeline generated file')
        f.close(output_verify='ignore')
        shutil.move(tmp1, self.output_filename) 
        log.debug("Image created : %s" % self.output_filename)

        return self.output_filename
                                    
################################################################################
# main
def main(arguments=None):
    # Get and check command-line options

    desc = """This module receives a series of FITS images (science)  and
creates the master super flat-field median combining images using sigma-clip algorithm."""

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("-s", "--source",
                  action="store", dest="source_file_list",
                  help="Source text file with list of full path of images.")

    parser.add_argument("-o", "--output",
                  action="store", dest="output_filename", 
                  help="Output file to write SuperFlat")
    
    # Not yet implemented
    # parser.add_argument("-b", "--bpm",
    #              action="store", dest="bpm", 
    #              help="Bad pixel map file [default=%default]", 
    #              default=None)

    parser.add_argument("-k", "--check",
                  action="store_true", dest="check", 
                  help="Check image properties (FILTER, EXPTIME, NCOADDS or READMODE)"
                  "[default: %(default)s]", default=False)

    parser.add_argument("-N", "--norm",
                  action="store_true", dest="norm", 
                  help="Normalize the output SuperFlat. If image is multi-chip"
                  ", normalization wrt chip 1 is done (default: %(default)s)",
                    default=False)

    parser.add_argument("-n", "--norm_estimator",
                  action="store", dest="norm_estimator", 
                  help="Robust estimator for normalization (median|robust_mean) (default: %(default)s)",
                  default="median")

    parser.add_argument("-m", "--median_smooth",
                  action="store_true", dest="median_smooth", default=False,
                  help="Median smooth the combined flat-field (default: %(default)s)")
                  

    options = parser.parse_args()
    
    if len(sys.argv[1:]) < 1:
       parser.print_help()
       sys.exit(0)
       
    if not options.source_file_list or not options.output_filename:
        # args is the leftover positional arguments after all options have been 
        # processed
        parser.print_help()
        parser.error("incorrect number of arguments " )
    
    filelist = [line.replace( "\n", "") for line in fileinput.input(options.source_file_list)]
    try:
        superflat = SuperSkyFlat(filelist, options.output_filename, 
                             None, options.norm, "/tmp/",
                             options.median_smooth, options.norm_estimator,
                             options.check)
        superflat.create()
    except Exception as e:
        log.error("Error: %s" % str(e))

######################################################################
if __name__ == "__main__":
    sys.exit(main())
