#!/usr/bin/env python

# Copyright (c) 2008-2015 IAA-CSIC  - All rights reserved. 
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
#
# PANICtool
#
# calDomeFlat.py
#
# Created    : 14/11/2008    jmiguel@iaa.es
# Last update: 29/09/2009    jmiguel@iaa.es
#              11/12/2009    jmiguel@iaa.es - Include the use of ClFits class, 
#                            and add filter name to the output filename
#              14/12/2009    jmiguel@iaa.es - Skip non DOME flats and cotinue 
#                            working with the good ones
#              12/02/2010    jmiguel@iaa.es - Check min number of dome flats
#              03/03/2010    jmiguel@iaa.es - Added READMODE checking 
#              17/11/2010    jmiguel@iaa.es - modified normalization by mode 
#                            (instead of mean) and added optional flag for it
#              27/03/2012    jmiguel@iaa.es  - Fixed bug wrt chip 1 normalization
#              03/12/2012    jmiguel@iaa.es  - Changed normalization by median instead of mode 
#
# 
# TODO:
#    - include BPM creation
#    - median smooth
# NOTE:
#    - A Bug in pyraf.mscred.mscarith required to modify src/mscarith.cl 
#      line# 25 in msarith.cl should be changed from 
#
#      int nop1, nop2, nresults, next1, next2, nexts, n 
#
#      to 
#
#      int nop1, nop2, nresult, next1, next2, nexts, n
#   More info: http://iraf.net/phpBB2/viewtopic.php?t=85010&sid=e2404ee77fcef3b0d8a744c47f853705
################################################################################
#
################################################################################
# Import necessary modules

import sys
import os
import fileinput
import time
import shutil
import argparse

# PAPI
from papi.misc.paLog import log
from papi.misc.fileUtils import removefiles
from papi.misc.utils import clock, listToFile
from papi.datahandler.clfits import ClFits, isaFITS
from papi.misc.collapse import collapse
import papi.misc.robust as robust
from papi.misc.version import __version__

# Pyraf modules
from pyraf import iraf
from iraf import noao
from iraf import mscred

# Interact with FITS files
import astropy.io.fits as fits
import numpy as np


class MasterDomeFlat(object):
    """
    Class used to build and manage a master calibration dome flat.
    
    Dome flats are not pretty good for low-spatial frequency QE variation 
    across the chip (large scale variation), but quite reasonable for 
    high-spatial frequency (small scale variations).
    
    
    Description:
    ------------ 
           
         1. Check the EXPTIME , TYPE(dome) and FILTER of each Flat frame
         2. Separate lamp ON/OFF dome flats
         3. Make the combine of Flat LAMP-OFF frames 
         4. Make the combine of Flat LAMP-ON frames
         5. Subtract lampON-lampOFF (implicit dark subtraction)
         6. (optionally) Normalize the flat-field with median (robust estimator)
            
            NOTE : We do NOT subtract any MASTER_DARK, it is not required for 
            DOME FLATS (it is done implicitly because both ON/OFF flats are taken 
            with the same Exposition Time).

        
    TODO:
    -----
        - Multiply by the BPM
        - Reject flat images when their background is different more than 1%
        compared to the other, or when more than 3 sigma of the others.
        - Optional Median smooth
    """
    
    def __init__(self, input_files, temp_dir="/tmp/",
                 output_filename="/tmp/mdflat.fits", normal=True,
                 median_smooth=False):
        """ 
        Initialization method
        
        Parameters
        ---------- 

        input_files : list
            A list of dome on/off flat fields
        temp_dir : string
            Temporal directory to use for temporal files
        output_filename : string
            Filename of the master dome flat to build.
        normal : bool
            If true, normalization will be done.
        median_smooth: bool
            If true, median smooth filter is applied to the combined Flat-Field
    
        """
        
        self.__input_files = input_files
        self.__temp_dir = temp_dir
        self.__output_filename = output_filename  # full filename (path+filename)
        self.__normal = normal
        self.__median_smooth = median_smooth
        
        self.MIN_FLATS = 1

    def createMaster(self):
      
        """
        Create a master Dome FLAT from the dome flat file list
        """   
        log.debug("Start createMasterDomeFlat")
        
        start_time = time.time()
        t = clock()
        t.tic()
    
        # Cleanup old files
        
        removefiles(self.__output_filename)
        domelist_lampon  = []
        domelist_lampoff = []
        
        # Get the user-defined list of flat frames
        if type(self.__input_files) == type(list()):
            framelist = self.__input_files  # list of sources files to be used in sky-flat computation
        elif os.path.isfile(self.__input_files):
            framelist = [line.replace( "\n", "") 
                         for line in fileinput.input(self.__input_files)]
        else:
            raise Exception("Cannot read source files")
        
        
        # Determine the number of Flats frames to combine
        try:
            nframes = len(framelist[0])
        except IndexError:
            log.error("No FLAT frames defined")
            raise 'No FLAT frames defined'

        if not os.path.exists(os.path.abspath(os.path.join(self.__output_filename, os.pardir))):
            log.error('Directory of combined FLAT frame does not exist')
            raise 'Directory of combined FLAT frame does not exist'
        if not self.__output_filename:
            log.error('Combined FLAT frame not defined')
            raise 'Combined FLAT frame not defined'
    
        
        # Change to the source directory
        base, infile   = os.path.split(self.__output_filename)
        iraf.chdir(base)
    
    
        # STEP 1: Check the EXPTIME , TYPE(dome) and FILTER of each Flat frame
        f_expt = -1
        f_type = ''
        f_filter = ''
        f_readmode = ''
        for iframe in framelist:
            f = ClFits ( iframe )
            log.debug("Flat frame %s EXPTIME= %f TYPE= %s FILTER= %s" %(iframe, f.expTime(),f.getType(), f.getFilter()))
            # Check EXPTIME
            if (f_expt != -1 and (int(f.expTime()) != int(f_expt) or
                                  f.getFilter()!=f_filter or 
                                  f.getReadMode()!=f_readmode)):
                log.warning("Found a FLAT frame with different FILTER or EXPTIME "
                    "or READMODE. Frame skipped !")
                continue
            else: 
                f_expt = f.expTime()
                if f.isDomeFlat():
                    f_filter = f.getFilter()
                    f_readmode = f.getReadMode()
                else:
                    log.error("Error,  frame %s does not look a Dome Flat field" %(iframe))
                    raise Exception("Error, frame %s does not look a Dome Flat field" %(iframe))
        
            # Separate lamp ON/OFF dome flats  
            if f.isDomeFlatON():
                domelist_lampon.append(iframe.replace("//", "/"))
            elif f.isDomeFlatOFF():
                domelist_lampoff.append(iframe.replace("//", "/"))
            else:
                log.warning("Found a FLAT frame with different Flat-Field type "
                    " It should be domeflat LAMP_ON/OFF. Frame skipped !")
        
        
        log.info('Right, all flat frames separated as:')
        log.info('DOME FLATS LAMP OFF (#%d) %s: ', len(domelist_lampon), domelist_lampon )
        log.info('DOME FLATS LAMP ON  (#%d) %s: ', len(domelist_lampoff), domelist_lampoff )
        log.info('Filter=%s , TEXP=%f ', f_filter, f_expt)
        
        if len(domelist_lampon) < self.MIN_FLATS:
            log.error("Error, not enough lamp_on flats. At least %s are required" %(self.MIN_FLATS))
            raise Exception("Error, not enough lamp_on flats. At least %s are required" %(self.MIN_FLATS))
        
        if len(domelist_lampoff) < self.MIN_FLATS:
            log.error("Error, not enough lamp_off flats. At least %s are required"%(self.MIN_FLATS))
            raise Exception("Error, not enough lamp_off flats. At least %s are required" %(self.MIN_FLATS))
    
        #Clobber existing output images
        iraf.clobber='yes'
        
        # NOTE : We do not subtract any MASTER_DARK, it is not required for 
        # DOME FLATS (it is done implicitly)
    
        # STEP 1.2: Check if images are cubes, then collapse them.
        domelist_lampon = collapse(domelist_lampon, out_dir=self.__temp_dir)
        domelist_lampoff = collapse(domelist_lampoff, out_dir=self.__temp_dir)
        
        # STEP 2: Make the combine of Flat LAMP-ON frames
        # - Build the frame list for IRAF
        log.debug("Combining Flat LAMP-ON frames...")
        flat_lampon = self.__temp_dir + "/flat_lampON.fits"
        removefiles(flat_lampon)
        listToFile(domelist_lampon, self.__temp_dir + "/files_on.list")
        # - Call IRAF task
        # Combine the images to find out the median using sigma-clip algorithm;
        # the input images are scaled to a common mode, the pixels containing 
        # objects are rejected by an algorithm based on the measured noise (sigclip).
        # For making a master flat, scale must always be set to 'mode'. (read from literature)
        iraf.mscred.flatcombine(input="@"+(self.__temp_dir+"/files_on.list").replace('//','/'),
                        output=flat_lampon,
                        combine='median',
                        ccdtype='',
                        process='no',
                        reject='sigclip',
                        subset='no',
                        scale='mode',
                        #verbose='yes'
                        #scale='exposure',
                        #expname='EXPTIME'
                        #ParList = _getparlistname ('flatcombine')
                        )
    
        # STEP 3: Make the combine of Flat LAMP-OFF frames
        # - Build the frame list for IRAF
        log.debug("Combining Flat LAMP-OFF frames...")    
        flat_lampoff = self.__temp_dir + "/flat_lampOFF.fits"
        removefiles(flat_lampoff)
        listToFile(domelist_lampoff, self.__temp_dir + "/files_off.list")
        # - Call IRAF task
        # Combine the images to find out the median using sigma-clip algorithm;
        # the input images are scaled to a common median, the pixels containing 
        # objects are rejected by an algorithm based on the measured noise (sigclip).
        iraf.mscred.flatcombine(input="@"+(self.__temp_dir + "/files_off.list").replace('//','/'),
                        output=flat_lampoff,
                        combine='median',
                        ccdtype='',
                        process='no',
                        reject='sigclip',
                        subset='no',
                        scale='mode', #robust estimator
                        #verbose='yes'
                        #scale='exposure',
                        #expname='EXPTIME'
                        #ParList = _getparlistname ('flatcombine')
                        )
    
        # STEP 4 : Subtract lampON-lampOFF (implicit dark subtraction)
        flat_diff = self.__temp_dir + "/flat_lampON_OFF.fits"
        log.debug("Subtracting Flat ON-OFF frames...%s", flat_diff) 
        # Remove an old masternormflat
        removefiles(flat_diff)
        
        # Single FITS are also supported by mscred.mscarith
        log.debug("Subtracting files...") 
        iraf.mscred.mscarith(operand1 = flat_lampon,
                    operand2=flat_lampoff,
                    op='-',
                    result=flat_diff
                    )
        
        # STEP 5: Normalize the flat-field (if MEF, normalize wrt chip SG1)
        # Compute the mean of the image
        if self.__normal:
            f = fits.open(flat_diff, ignore_missing_end=True)
            f_instrument = f[0].header['INSTRUME'].lower()
            if len(f) > 1:
                ##chip = 1 # normalize wrt to mode of chip SG1_1
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
                
                naxis1 = f[ext_name].header['NAXIS1']
                naxis2 = f[ext_name].header['NAXIS2']
                offset1 = int(naxis1 * 0.1)
                offset2 = int(naxis2 * 0.1)
                # Note that in Numpy, arrays are indexed as rows X columns (y, x),
                # contrary to FITS standard (NAXIS1=columns, NAXIS2=rows).
                median = np.median(f[ext_name].data[offset2 : naxis2 - offset2,
                                                    offset1 : naxis1 - offset1])
                msg = "Normalization of MEF master flat frame wrt chip %s. (MEDIAN=%d)"%(ext_name,median)
            elif ('INSTRUME' in f[0].header and f[0].header['INSTRUME'].lower() == 'panic'
                  and f[0].header['NAXIS1'] == 4096 and f[0].header['NAXIS2'] == 4096):
                if 'H2RG' in f[0].header['CAMERA']:
                    # It supposed to have a full frame of PANIC in one single 
                    # extension (GEIRS default). Normalize wrt detector SG1_1
                    median = np.median(f[0].data[200 : 2048-200, 2048+200 : 4096-200 ])
                    msg = "Normalization of (full-H2RG) PANIC master flat frame wrt chip 1. (MEDIAN=%d)" % median
                elif 'H4RG' in f[0].header['CAMERA']:
                    # It supposed to have a full frame of PANIC-H4RG in one single 
                    # extension; Normalize wrt center of detector.
                    median = np.median(f[0].data[200 : 4096-200, 200 : 4096-200 ])
                    msg = "Normalization of (full-H4RG) PANIC master flat frame (MEDIAN=%d)" % median
            else:
                # Not MEF, not PANIC full-frame, but could be a PANIC subwindow
                naxis1 = f[0].header['NAXIS1']
                naxis2 = f[0].header['NAXIS2']
                offset1 = int(naxis1 * 0.1)
                offset2 = int(naxis2 * 0.1)
                median = np.median(f[0].data[offset2 : naxis2 - offset2,
                                             offset1 : naxis1 - offset1])
                msg = "Normalization of master flat frame. (MEDIAN=%d)"%median 
 

            f.close()
            log.debug(msg)
            
            # Cleanup: Remove temporary files
            removefiles(self.__output_filename)
            # Compute normalized flat
            iraf.mscred.mscarith(operand1=flat_diff,
                    operand2=median,
                    op='/',
                    pixtype='real',
                    result=self.__output_filename.replace("//","/"),
                    )
        else:
            shutil.move(flat_diff, self.__output_filename)
        
                        
        # STEP 6 ##: (optional)
        # Median smooth the master (normalized) flat
        if self.__median_smooth:
            log.debug("Doing Median smooth of FF ...")
            iraf.mscmedian(
                    input=self.__output_filename,
                    output=self.__output_filename.replace(".fits","_smooth.fits").replace("//","/"),
                    xwindow=20,
                    ywindow=20,
                    outtype="median"
                    )
            shutil.move(self.__output_filename.replace(".fits", "_smooth.fits"),
                        self.__output_filename)


        # Change back to the original working directory
        iraf.chdir()
        
        log.debug("Updating the header ...")
        flatframe = fits.open(self.__output_filename, 'update')
        if self.__normal: 
            flatframe[0].header.add_history('Computed normalized master dome flat (lamp_on-lamp_off)' )
            if msg != "":
                flatframe[0].header.add_history(msg)
        else:
            flatframe[0].header.add_history('Computed master dome flat (lamp_on-lamp_off)' )
        
        flatframe[0].header.add_history('lamp_on  files: %s' %domelist_lampon )
        flatframe[0].header.add_history('lamp_off files: %s' %domelist_lampoff )
        # Add a new keyword-->PAPITYPE
        flatframe[0].header.set('PAPITYPE', 'MASTER_DOME_FLAT', 
                                   'TYPE of PANIC Pipeline generated file')
        flatframe[0].header.set('PAPIVERS', __version__, 'PANIC Pipeline version')
        flatframe[0].header.set('IMAGETYP', 'MASTER_DOME_FLAT', 
                                   'TYPE of PANIC Pipeline generated file')
        if 'PAT_NEXP' in flatframe[0].header:
            flatframe[0].header.set('PAT_NEXP', 1,
                                             '# of positions into dither pattern')

        # This ignore any FITS standar violation and allow write/update the
        # FITS file
        flatframe.close(output_verify='ignore')

        # Cleanup: Remove temporary files
        # misc.fileUtils.removefiles(flat_lampoff, flat_lampon, flat_diff)
        # Remove temp list files
        removefiles(self.__temp_dir + "/files_off.list")
        removefiles(self.__temp_dir + "/files_on.list")

        log.debug(t.tac() )
        log.debug('Saved master FLAT to %s' ,  self.__output_filename )
        
        return self.__output_filename
        
################################################################################
# main
def main(arguments=None):

    desc = """This module receives a series of Dome Flats (On and Off) and
then creates a Master Dome Flat-Field. It does **not** require any Master Dark.
"""
    parser = argparse.ArgumentParser(description=desc)
                  
    parser.add_argument("-s", "--source",
                  action="store", dest="source_file_list",
                  help="Source file list of data frames."
                  " It can be a file or directory name.")
    
    
    parser.add_argument("-o", "--output",
                  action="store", dest="output_filename", 
                  help="Final coadded output image")
    
    ## -optional
    
    """parser.add_option("-b", "--master_bpm",
                  action="store", dest="master_bpm",
                  help="Bad pixel mask to be used (optional)", default=None)
    """
    parser.add_argument("-N", "--normalize",
                  action="store_true", dest="normalize", default=False,
                  help="Normalize master flat by median. "
                  "If image is multi-detector, then normalization"
                  " wrt chip 1 is done) [default=%(default)s].")

    parser.add_argument("-m", "--median_smooth",
                  action="store_true", dest="median_smooth", default=False,
                  help="Median smooth the combined flat-field [default=%(default)s]")

    options = parser.parse_args()
    
    if len(sys.argv[1:]) < 1:
       parser.print_help()
       sys.exit(0)
    
    if not options.source_file_list or not options.output_filename:
        parser.print_help()
        parser.error("incorrect number of arguments " )
    
    
        
    filelist = [line.replace( "\n", "") for line in
                fileinput.input(options.source_file_list)]

    tmp_dir = os.path.abspath(os.path.join(options.output_filename, os.pardir))
    mDFlat = MasterDomeFlat(filelist, tmp_dir, options.output_filename, 
                            options.normalize, options.median_smooth)
    mDFlat.createMaster()

######################################################################
if __name__ == "__main__":
    sys.exit(main())
