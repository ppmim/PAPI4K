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

################################################################################
#
# PANICtool
#
# calDark.py
#
# Created    : 07/11/2008    jmiguel@iaa.es
# Last update: 29/09/2009    jmiguel@iaa.es - Scale by EXPTIME
#              11/12/2009    jmiguel@iaa.es - Rename output filename to include 
#                            EXPTIME and NCOADDS and use ClFits class
#              14/12/2009    jmiguel@iaa.es - Skip non DARK frames and continue 
#                            working with the good ones (good_frames)
#              02/03/2010    jmiguel@iaa.es - added READEMODE checking
#              14/09/2010    jmiguel@iaa.es - added support to MEF files, 
#                            calling mscred.darkcombine subrutine instead of 
#                            imred.darkcombine
#              07/03/2011    jmiguel@iaa.es - Added Stats output and 
#                            normalization (divide master dark by the TEXP to 
#                            get a master dark in ADU/s units)
#
# TODO
#  - checking of ITIME ( and not only EXPTIME, NCOADDS )
################################################################################

################################################################################
# Import necessary modules

import sys
import os
import fileinput
import shutil
import argparse
import numpy 

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
from iraf import mscred

# Interact with FITS files
from astropy.io import fits


class MasterDark(object):
    """
    Create a master Dark from a list for dark files (single or MEF files); all
    must have the same properties (TEXP, NCOADDS, READMODE).
    
    Parameters
    ----------
    
    file_list : list
        A list of dark files
    temp_dir: str
        Directory where temp files will be created
    output_filename: str
        Ouput filename of the master dark file to be created
    texp_scale: bool
        If true, scale the darks before the combination.
    bpm: str
        Bad pixel Map filename
    normalize: str
        Whether true, a normalization to 1 second is done after darks combination.
        It means, the master dark is supposed to have the count level of a
        dark frame of 1 second.
    show_stats: bool
        Whether true, some statistics will be be shown
    no_type_checking: bool
        Whether true, the type of file (dark, flat, ...) will no be checked
        in the input files
    """
    def __init__(self, file_list, temp_dir, output_filename="/tmp/mdark.fits",
                 texp_scale=False, bpm=None, normalize=False,
                 show_stats=False, no_type_checking=False):
        """
        Initialize the object
        """
        
        self.__file_list = file_list
        self.__output_filename = output_filename  # full filename (path+filename)
        self.__temp_dir = temp_dir #temporal dir used for temporal/intermediate files
        self.__bpm = bpm
        self.m_min_ndarks = 3
        self.m_texp_scale = texp_scale # see note below
        self.m_normalize = normalize
        self.show_stats = show_stats
        self.no_type_checking = no_type_checking
        
    def createMaster(self):
      
        """
        Create a master DARK from the dark file list.
        
        Warns
        -----
        The method must be called only after the object was properly initialized.
        """
           
        log.debug("Start createMaster")
        t = clock()
        t.tic()

        # Get the user-defined list of dark frames
        framelist = self.__file_list
        
        # STEP 0: Determine the number of darks frames to combine
        try:    
            nframes = len(framelist)
        except IndexError as e:
            log.error("No DARK frames defined")
            raise e
        
        if nframes < self.m_min_ndarks:
            log.error("Not enough number of dark frames (>%s) to compute master dark: %s",self.m_min_ndarks, framelist)
            raise Exception("Not enough number of dark frames (>=%s) to compute master dark" %(self.m_min_ndarks))
            
            
        if not os.path.exists(os.path.abspath(os.path.join(self.__output_filename, os.pardir))):
            raise NameError('Wrong output path')
        if not self.__output_filename:
            log.error("Combined DARK frame not defined")
            raise Exception("Wrong output filename")
    
        # Change to the source directory
        base, infile = os.path.split(self.__output_filename)
        iraf.chdir(base)
    
        
        # STEP 1: Check the EXPTIME, TYPE(dark) of each frame
        f_expt = -1.0
        f_type = ''
        f_ncoadds = -1
        f_readmode = -1
        good_frames = []

        for iframe in framelist:
            f = ClFits(iframe)
            log.debug("Frame %s EXPTIME= %f TYPE= %s NCOADDS= %s REAMODE= %s" 
                      %(iframe, f.expTime(), f.getType(), f.getNcoadds(), 
                        f.getReadMode()))
            if not self.no_type_checking and not f.isDark():
                log.error("Error: Task 'createMasterDark' finished. Frame %s is not 'DARK'",iframe)
                raise Exception("Found a non DARK frame") 
                # continue
            else:        
                # Check EXPTIME, TYPE(dark) and READMODE
                if (not self.m_texp_scale and f_expt != -1 and 
                     (int(f.expTime()) != int(f_expt) or  
                      f.getType() != f_type or 
                      f.getNcoadds() != f_ncoadds or 
                      f.getReadMode() != f_readmode)):
                    log.error("Error: Task 'createMasterDark' finished. Found a DARK frame (%s)with different EXPTIME, NCOADDS or READMODE",iframe)
                    #continue
                    raise Exception("Found a DARK frame with different EXPTIME or NCOADDS or READMODE") 
                else: 
                    f_expt  = f.expTime()
                    f_ncoadds = f.getNcoadds()
                    f_type = f.getType()
                    f_readmode = f.getReadMode()
                    good_frames.append(iframe.replace("//", "/"))
                                        
        log.debug('Right, dark frames with same type are: %s', good_frames)   
    
        if self.m_texp_scale:
            scale_str = 'exposure'
        else:
            scale_str = 'none'
        
        
        # Cleanup : Remove old masterdark
        removefiles(self.__output_filename)
        tmp1 = self.__temp_dir + "/dark_tmp.fits"
        removefiles(tmp1)
        
        # Add TEXP and NCOADD to master filename
        if f_ncoadds == -1:
            f_ncoadds = 1
        self.__output_filename = self.__output_filename.replace(".fits",
                                                                "_%d_%d.fits" % (f_expt, f_ncoadds))
        
    
        # STEP 1.2: Check if images are cubes, then collapse them.
        good_frames = collapse(good_frames, out_dir=self.__temp_dir)
        
        # Write frames to txt file
        listToFile(good_frames, self.__temp_dir + "/files.list")
        
        """
        NOTE: I don't know how darkcombine does the scaling with EXPTIME, in
        #fact --> see F.Vales email : 
        #http://iraf.net/phpBB2/viewtopic.php?p=138721
        http://iraf.net/phpBB2/viewtopic.php?p=86769&sid=65b3c9990c92749c317ab554a01c8da7
        """
        """
        If we decide to scale the dark by exposure time, we will have to have 
        the bias subtracted. (You can do this by turning the "process" option on.) 
        Otherwise, the bias will end up being scaled, too. Once again, keep 
        in mind that running ccdproc with the resultant darks will cause the 
        bias to be subtracted again; you have to be very careful.
        """

        # Call the iraf.mscred.darkcombine task through PyRAF
        iraf.mscred.darkcombine(input = "@"+(self.__temp_dir+"/files.list").replace('//','/'),
                        output=tmp1.replace('//','/'),
                        combine='average',
                        ccdtype='',
                        process='no',
                        reject='minmax',
                        nlow='0',
                        nhigh='1',
                        nkeep='1',
                        blank='INDEF',
                        scale=scale_str,
                        #expname = 'EXPTIME'
                        #ParList = _getparlistname('darkcombine')
                        )
         
        if self.m_normalize:
            log.debug("Normalizing master dark to 1 sec")
            # divide master dark by the TEXP to get a master dark in ADU/s units
            texp = ClFits(tmp1).expTime()
            iraf.mscred.mscarith(operand1 = tmp1,
                                 operand2 = texp,
                                 op='/',
                                 result=self.__output_filename,
                                 verbose='no')
        else:
            shutil.move(tmp1, self.__output_filename)
    
        darkframe = fits.open(self.__output_filename,'update')
        # Add a new keyword-->PAPITYPE
        darkframe[0].header.set('PAPITYPE','MASTER_DARK','TYPE of PANIC Pipeline generated file')
        darkframe[0].header.set('PAPIVERS', __version__, 'PANIC Pipeline version')
        darkframe[0].header.set('IMAGETYP','MASTER_DARK','TYPE of PANIC Pipeline generated file')
        if 'PAT_NEXP' in darkframe[0].header:
            darkframe[0].header.set('PAT_NEXP', 1, 'Number of position into the current dither pattern')
        if self.m_normalize:
            darkframe[0].header.set('EXPTIME', 1.0)
            darkframe[0].header.set('ITIME', 1.0)
            darkframe[0].header.set('NCOADDS', 1)
        
        # 'ignore' will ignore any FITS standard violation and allow 
        # write/update the FITS file
        darkframe.close(output_verify='ignore')     
        
        log.debug('Saved master DARK to %s', self.__output_filename)
        log.debug("createMasterDark' finished %s", t.tac() )
        
        if self.show_stats:
            medians = []
            for i_frame in good_frames:
                pf = fits.open(i_frame)
                x1, y1 = pf[0].data.shape
                if len(pf) == 1:
                    # print "mean=",numpy.mean(pf[0].data[512:1536,512:1536])
                    medians.append(robust.r_nanmedian(pf[0].data[int(x1*0.25) : int(y1*0.75), int(x1*0.25) : int(y1*0.75)]))
                else:
                    print("MEF files now are supported !")
                    for i_ext in range(1, len(pf)):
                        medians.append(robust.r_nanmedian(pf[i_ext].data[int(x1*0.25) : int(y1*0.75), int(x1*0.25) : int(y1*0.75)]))
                
                # Get some stats from master dark (mean/median/rms)
                print("I_FRAME=", i_frame)
                values = (iraf.mscstat(images=i_frame,
                                fields="image,mean,mode,midpt,stddev,min,max",
                                format='yes',Stdout=1))
                for line in values:
                    print(line)
            print("-----------------------------------")
            print("MEDIANS of center of detector (robust) =", medians)
            print("QC DARK MEAN =", numpy.mean(medians))
            print("QC DARK MED =", numpy.median(medians))
            print("QC DARK STDEV =", numpy.std(medians))
            print("QC DARK MAD =", numpy.median(numpy.abs(medians - numpy.median(medians))))
            
            #print "QC RONi",
            #print "QC DARK NBADPIX =", 
            
                  
            # Get some stats from master dark (mean/median/rms)
            print("Master dark Stats:")
            print("------------------")
            values = (iraf.mscstat (images=self.__output_filename,
                                    fields="image,mean,mode,stddev,min,max",
                                    format='yes',Stdout=1))
            for line in values:
                print(line)
            
        return self.__output_filename
        

################################################################################
# main
def main(arguments=None):
    # Get and check command-line options
    # The script doesnt take any positional arguments, so only options
    desc = """This module receives a series of FITS images (darks) and
creates the master dark and computes several statistics.
"""
    parser = argparse.ArgumentParser(description=desc)
    
                  
    parser.add_argument("-s", "--source",
                  action="store", dest="source_file_list",
                  help="Source file listing the filenames of dark frames.")
    
    parser.add_argument("-o", "--output",
                  action="store", dest="output_filename", 
                  help="final coadded output image")
    
    parser.add_argument("-n", "--normalize",
                  action="store_true", dest="normalize", default=False,
                  help="normalize master dark to 1 sec [default False]")
    
    parser.add_argument("-e", "--scale",
                  action="store_true", dest="texp_scale", default=False,
                  help="scale raw frames by TEXP [default False]")
   
    parser.add_argument("-S", "--show_stats",
                  action="store_true", dest="show_stats", default=False,
                  help="Show frame stats [default False]")    
    
    parser.add_argument("-t", "--no_type_checking",
                  action="store_true", dest="no_type_checking", default=False,
                  help="Do not make frame type checking [default False]")    
    
    parser.add_argument("-v", "--verbose",
                  action="store_true", dest="verbose", default=True,
                  help="verbose mode [default]")
    
    options = parser.parse_args()
   
    if len(sys.argv[1:]) < 1:
       parser.print_help()
       sys.exit(0)

    if not options.source_file_list or not options.output_filename:
        parser.print_help()
        parser.error("incorrent number of arguments")
    
    if (os.path.isdir(options.source_file_list) or
            os.path.isdir(options.output_filename)):
        parser.print_help()
        parser.error("Source and output must be a file, not a directory")
        
    filelist = [line.replace("\n", "")
                for line in fileinput.input(options.source_file_list)]
    
    try:
        mDark = MasterDark(filelist, "/tmp", options.output_filename, 
                           options.texp_scale, None, options.normalize,
                           options.show_stats, options.no_type_checking)
        mDark.createMaster()
    except Exception as e:
        log.error("Task failed. Some error was found: %s" % str(e))

######################################################################
if __name__ == "__main__":
    sys.exit(main())
