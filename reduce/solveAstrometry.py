#! /usr/bin/env python
#encoding:UTF-8

# Copyright (c) 2013 Jose M. Ibanez All rights reserved.
# Institute of Astrophysics of Andalusia, IAA-CSIC
#
# This file is part of PAPI and OSN-CCDs astrometry procedures
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



from __future__ import division

import sys
import os
import shutil
import fileinput
import logging
import subprocess
import multiprocessing
import glob
import argparse
from distutils import spawn

import time
import re

# Project modules
from astropy import wcs
import astropy.io.fits as fits
import numpy
import papi.misc.robust as robust
from papi.misc.paLog import log as logging


try: 
    import clfits
except ImportError:
    import papi.datahandler.clfits as clfits

# TODO
#
# - Add support for MEF files:
#   Currently Astrometry.net only support --extension option to give the FITS 
#    extension to read image from.
# - Tiempo límite de resolución de un fichero --cpulimit (default to 300s)
# - Opcion de añadir header wcs a la cabecera (image.new) 
# - Estadísicas de errores de calibracion
# - distorsion promedio (encontre un mail de Dustin donde hablaba de eso)
# - calibracion "fuerza bruta" 
# - log file



def readHeader(filename, extension=1):
    """
    Read from the FITS header values required for astrometric calibration.
    If input file is a MEF, extension[1,N] must be specified.
    
    Parameters
    ----------
    
    filename: str
        File name of the file to read.
    
    extension: int
        For MEF files, extension number to use. If input file is
        not a MEF, then 'extesion' has no effect.
    
    """
        
    try:
        myfits = clfits.ClFits(filename)
    except Exception as e:
        msg = "Error reading FITS file: " + filename
        logging.error(msg)
        logging.error(str(e))
        raise e
    else:
        if myfits.isMEF():
            logging.info("Found a MEF file. Extension to use = %s" % extension)
            m_wcs = wcs.WCS(fits.getheader(filename, ext=int(extension)))
            # No SIP or Paper IV table lookup distortion correction is applied.
            ra = m_wcs.wcs_pix2world([[myfits.naxis1/2, myfits.naxis2/2]], 1)[0][0]
            dec = m_wcs.wcs_pix2world([[myfits.naxis1/2, myfits.naxis2/2]], 1)[0][1]
        else:
            ra = myfits.ra
            dec = myfits.dec

        # Return values
        scale = myfits.pix_scale
        instrument = myfits.getInstrument()
        is_science = myfits.isScience()
        naxis1 = myfits.naxis1
        naxis2 = myfits.naxis2

        return scale, ra, dec, instrument, is_science, naxis1, naxis2
        
    
def solveField(filename, out_dir, tmp_dir="/tmp", pix_scale=None, extension=0, downsample=1):
    """
    Do astrometric calibration to the given filename using Astrometry.net 
    function 'solve-field'.
    Currently (Feb-2014), "4200-series" (2MASS) index files are being used,
    locally installed on the computer.

    
    Parameters
    ----------
    filename: str
        Filename of the frame to solve; cannot be a MEF file, Astrometry.net
        only supports MEF files with the option --extension. 
        
    out_dir: str
        Directory where out files are saved.
        
    tmp_dir: str
        Directory where temp files of solve-field are saved and then deleted.

    pix_scale: float
        Default pixel scale to use in case it cannot be find out from header

    extension: int
        In case of MEF file, extension to be used to solve field. Default 0
        extension means 'no-mef', and thus one single extension.

    Returns
    -------
    Filename of solved file (filename.new.fits) 
    """
    
    logging.debug("Entering solveField...")
    #
    # Create temporal and or output directory
    #    
    if not os.path.isdir(tmp_dir):
        os.makedirs(tmp_dir)
    
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    
    # Check the number of NaNs: Astrometry.net may fail if a large number of 
    # NAN pixels is present. In this case, NaNs are replaced by mean value
    # in order to run the astrometric calibration. After that, we revert
    # the NAN values.
    MAX_N_NAN = 10000
    nan_replaced = False
    try:
        with fits.open(filename, 'update') as hdu:
            n_nan = numpy.count_nonzero(numpy.isnan(hdu[extension].data))
            logging.info("Number of NANs found: %d" % n_nan)
            if n_nan > MAX_N_NAN:
                median = robust.r_nanmean(hdu[extension].data)
                logging.info("Replacing NANs with median value : %f" % median)
                p_nan = numpy.isnan(hdu[extension].data)
                hdu[extension].data[p_nan] = median
                hdu.flush()
                hdu.close()
                #fits.writeto(filename, hdu[extension].data, header=hdu[0].header, clobber=True)
                nan_replaced = True
    except Exception as e:
        print("Error...:%s"%str(e))

    
    #
    # Read header parameters
    #    
    (scale, ra, dec, instrument, is_science, nx1, nx2) = readHeader(filename, extension)
    # Whether no scale was found out and some was given as default, we use it
    if scale == -1 and pix_scale:
        scale = pix_scale
    
    # Extension paramter
    if extension > 0:
        ext_str = "--extension %d" % int(extension)
    else:
        ext_str = ""
        
    if not is_science:
        logging.info("Frame %s is not a science frame" % filename)
        
    logging.debug("Starting to solve-field for: %s  Scale=%s  RA= %s Dec= %s \
    INSTRUMENT= %s" % (filename, scale, ra, dec, instrument))
    
    try:
        path_astrometry = os.path.dirname(spawn.find_executable("solve-field"))  
    except Exception:
        msg = "Cannot find the pathname for solve-field"
        logging.error(msg)
        raise Exception(msg)
    
    if not os.path.exists(path_astrometry + "/solve-field"):
        raise Exception("[solveAstrometry] Error, cannot find Astrometry.net binaries in %s" % path_astrometry)


    # To optimize the finding and CPU time required
    if nx1 == 4096 and nx2 == 4096:
        downsample = 2
    else:
        downsample = downsample

    #
    # We must distinguish different cases
    #
    # 1) RA, Dec and Scale are known
    if ra != -1 and dec != -1 and scale != -1:
        logging.debug("RA, Dec and Scale are known")
        # To avoid problems with wrong RA,Dec coordinates guessed, a wide 
        # radius is used (0.5 degrees)
        # Although --downsample is used, scale does not need to be modified
        str_cmd = "%s/solve-field -O -p --tweak-order 1 --scale-units arcsecperpix --scale-low %s \
        --scale-high %s --ra %s --dec %s --radius 0.5 -D %s --temp-dir %s %s %s --downsample %s\
        "%(path_astrometry, scale-0.05, scale+0.05, ra, dec, out_dir, tmp_dir, filename, ext_str, downsample)
    # 2) RA, Dec are unknown but scale is
    elif ra == -1 or dec == -1:
        logging.debug("RA, Dec are unknown but scale is")
        str_cmd = "%s/solve-field -O -p --scale-units arcsecperpix --scale-low %s \
        --scale-high %s -D %s --temp-dir %s %s %s --downsample %s\
        "%(path_astrometry, scale - 0.1, scale + 0.1, out_dir, tmp_dir, filename, ext_str, downsample)
    # 3) None is known -- blind calibration
    if (ra == -1 or dec ==- 1) and scale == -1:
        logging.debug("Nothing is known")
        str_cmd = "%s/solve-field -O -p -D %s --temp-dir %s %s %s --downsample %s\
        " % (path_astrometry, out_dir, tmp_dir, filename, ext_str, downsample)
    
    logging.debug("CMD=" + str_cmd)
    print("CMD_Astrometry.net =", str_cmd)

    try:
        p = subprocess.Popen(str_cmd, bufsize=0, shell=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             close_fds=True)
    except Exception as e:
        logging.error("Some error while running subprocess: " + str_cmd)
        logging.error(str(e))
        raise e

    # Warning:
    # We use communicate() rather than .stdin.write, .stdout.read or .stderr.read 
    # to avoid deadlocks due to any of the other OS pipe buffers filling up and 
    # blocking the child process.(Python Ref.doc)

    (stdoutdata, stderrdata) = p.communicate()
    solve_out = stdoutdata.decode() + "\n" + stderrdata.decode()

    if len(solve_out) > 1:
        logging.info("Solve-field output:" + solve_out)

    #
    # Look for filename.solved to know if field was solved
    #
    solved_file = os.path.join(out_dir, 
        os.path.splitext(os.path.basename(filename))[0] + ".solved")

    if os.path.exists(solved_file):
        logging.info("Field solved !")
        new_file = os.path.join(out_dir, os.path.splitext(os.path.basename(filename))[0] + ".new")
        out_file = new_file.replace(".new", ".ast.fits")
        shutil.move(new_file, out_file)
        
        # Revert NANs values
        if nan_replaced:
            with fits.open(out_file, 'update') as hdu:
                logging.info("Reverting NANs...")
                hdu[0].data[p_nan] = numpy.NaN
                #fits.writeto(out_file, hdu[0].data, header=hdu[0].header, clobber=True)
                hdu.flush()
                hdu.close()
                
        # Get rotation angle
        # Extract rotation angle from a line like the following one:
        # Field rotation angle: up is 0.214027 degrees E of N
        # (code from vterron)
        ROT_ANGLE = "Unknown"
        float_regexp = r"[-+]?\d*\.\d+|\d+"
        regexp = "Field rotation angle: up is ({0}) degrees".format(float_regexp)
        
        match = re.search(regexp, solve_out)
        if match:
            ROT_ANGLE = float(match.group(1))
                
        logging.info("ROT_ANGLE = %s" % ROT_ANGLE)
        
        # Write value into fits header
        fits.setval(out_file, keyword="ROTANGLE", value=ROT_ANGLE, comment="degrees E of N", ext=0)
        
        # in any case try to remove the files created by astrometry.net
        try:
            basename = os.path.join(out_dir, os.path.splitext(os.path.basename(filename))[0])
            cleanUp(basename)
            # Cannot delete tmp.sanitized.* (that are not removed by astrometry.net)
            # because we cannot distinguish which ones belong to the current 
            # execution, and we could be removing tmp.sanitized files from current
            # in parallel executions.
            #for fl in glob.glob(tmp_dir + "/tmp.sanitized.*"):
            #    os.remove(fl)
        except Exception as e:
            logging.warning("Some error while deleting temporal files for file %s"%filename)
            
        return out_file
    
    else:
        logging.error("Field was not solved.")
        raise Exception("Field was not solved.")
    
    
    
           
def cleanUp(path):
    """
    Remove all output files generated by astrometry.net,
    less the new .fits file.
    
    Parameters
    ----------
    path: path of the files to be removed. It can be a directory 
        or a base filename.
    
    extensions: [axy, corr, xyls, .match, .rdls, .solved, .wcs]
    
    """
    extensions = ['.axy', '.corr', '-indx.xyls', '.match', '.rdls', '.solved', '.wcs']
    
    if path.endswith("/"):
        # is a directory
        path = path + "*"
    else:
        # is a base filename
        pass
    
    for ext in extensions:
        fl = path + ext
        try:
            os.remove(fl)
        except Exception:
            pass


def calc(args):
    """
    Method used only to use with Pool.map_asycn() function

    Returns
    -------
    On succes, the filename with the solved field.

    """
    return solveField(*args)


def runMultiSolver(files, out_dir, tmp_dir, pix_scale=None, extension=0, downsample=1):
    """
    Run a parallel proceesing to solve astrometry for the input files taking
    advantege of multi-core CPUs.

    Returns
    -------
    On succes, a list with the filenames of the fields solved.
    """

    # use all CPUs available in the computer
    n_cpus = multiprocessing.cpu_count()
    logging.debug("N_CPUS :" + str(n_cpus))
    pool = multiprocessing.Pool(processes=n_cpus)
    
    results = []
    solved = []
    for file in files:
        logging.debug("File: %s" % file)
        red_parameters = (file, out_dir, tmp_dir, pix_scale, extension, downsample)
        try:
            # Instead of pool.map() that blocks until
            # the result is ready, we use pool.map_async()
            results += [pool.map_async(calc, [red_parameters])]
        except Exception as e:
            logging.error("Error processing file: " + file)
            logging.error(str(e))
            
    for result in results:
        try:
            result.wait()
            # the 0 index is *ONLY* required if map_async is used !!!
            solved.append(result.get()[0])
            logging.info("New file created => %s"%solved[-1])
        except Exception as e:
            logging.error("Cannot process file \n" + str(e))
            
    
    # Here we could try again to solve fields that were not solved but
    # using other parameters or index files


    # Prevents any more tasks from being submitted to the pool. 
    # Once all the tasks have been completed the worker 
    # processes will exit.
    pool.close()

    # Wait for the worker processes to exit. One must call 
    #close() or terminate() before using join().
    pool.join()
    
    logging.info("Finished parallel calibration")
    
    return solved
                  
###############################################################################
# main
###############################################################################
def main(arguments=None):

    # Get and check command-line options
    usage = "usage: %prog [options] arg1 arg2 ..."
    desc = """Performs the astrometric calibration of a set of images,
in principle previously reduced, but not mandatory; Astromety.net tool is used.

"""
    parser = argparse.ArgumentParser(description=desc)
    
                  
    parser.add_argument("-s", "--source",
                  action="store", dest="source_file",
                  help="Source file list of data frames. "
                  "It can be a file or directory name.")
    
    parser.add_argument("-o", "--output_dir",
                  action="store", dest="output_dir", default="/tmp",
                  help="Place all output files in the specified directory [default: %(default)s]")
    
    parser.add_argument("-t", "--temp_dir",
                  action="store", dest="temp_dir", default="/tmp",
                  help="Place all temp files in the specified directory [default: %(default)s]")
    
    parser.add_argument("-p", "--pixel_scale",
                  action="store", dest="pixel_scale", type=float, 
                  help="Pixel scale of the images")

    parser.add_argument("-d", "--downsample",
                  action="store", dest="downsample", type=int, default=2, 
                  help="Downsample the image by factor (int>0) before running solve")
    
    parser.add_argument("-e", "--extension",
                  action="store", dest="extension", type=int, default=0,
                  help="If file is a MEF, extension to be used for solving the field ("
                  "1=SG1, 2=SG2, 3=SG3, 4=SG4, 0=non MEF)")
                  
    parser.add_argument("-r", "--recursive",
                  action="store_true", dest="recursive", default=False,
                  help="Recursive subdirectories if source is a directory name (only first level)")
    
                                
    options = parser.parse_args()

    files_solved = []
    files_not_solved = []
    
    # args is the leftover positional arguments after all options have been processed
    if not options.source_file or len(sys.argv[1:]) < 1:
        parser.print_help()
        parser.error("incorrect number of arguments " )
    
    tic = time.time()

    # Check if source_file is a FITS file or a text file listing a set of files
    if os.path.exists(options.source_file):
        if os.path.isfile(options.source_file):
            try:
                hdulist = fits.open(options.source_file)
                filelist = [options.source_file]
            except:
                filelist = [line.replace("\n", "") 
                            for line in fileinput.input(options.source_file)]
        elif os.path.isdir(options.source_file):
            filelist = glob.glob(options.source_file + "/*.fit*")
            # Look for subdirectories
            if options.recursive:
                subdirectories = [ name for name in os.listdir(options.source_file) \
                    if os.path.isdir(os.path.join(options.source_file, name)) ]
                for subdir in subdirectories:
                    filelist += glob.glob(os.path.join(options.source_file, subdir) + "/*.fit*")
                
        # Parallel approach        
        files_solved = runMultiSolver(filelist, 
                                      options.output_dir,
                                      options.temp_dir,
                                      options.pixel_scale,
                                      options.extension,
                                      options.downsample)
        for file in filelist:
            ren_file = os.path.join(options.output_dir,
                    os.path.basename(os.path.splitext(file)[0] + ".ast.fits"))
            if ren_file not in files_solved and file + ".not_science" not in files_solved:
                files_not_solved.append(file)
        
        # Serial approach
                    
        #for file in filelist:
        #    try:
        #        solveField(file, options.output_dir, options.pixel_scale)
        #        files_solved.append(file)                
        #    except Exception,e:
        #        files_not_solved.append(file)
        #        logging.error("Error solving file %s  [%s] "%(file,str(e)))
                    
    else:
        logging.error("Source file %s does not exists", options.source_file)
        sys.exit()

    toc = time.time()

    logging.info("No. files = %s" % len(filelist))
    # calibracion files (bias, dark, flats, ...) are considered as solved files
    logging.info("No. files solved = %s"%(len(filelist) - len(files_not_solved)))
    logging.info("----------------")
    logging.info(files_solved)
    print("\n")
    logging.info("No. files NOT solved = %s", len(files_not_solved))
    logging.info("--------------------")
    logging.info(files_not_solved)
    logging.info("Time : %s"%(toc-tic))

    sys.exit()

######################################################################
if __name__ == "__main__":
    sys.exit(main())
