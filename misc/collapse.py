#!/usr/bin/env python

# Copyright (c) 2012 IAA-CSIC  - All rights reserved. 
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



# Import necessary modules
import argparse
import sys
import os
import astropy.io.fits as fits
import fileinput
import numpy

from papi.misc.paLog import log
from papi.misc.version import __version__


def collapse(frame_list, out_dir="/tmp", mean=False, start=0, end=-1):
    """
    Collapse (add them up arithmetically) a (list) of data cubes into a single 
    2D image. Files can be MEF or Single.


        Parameters
        ----------
        frame_list : list
            list of fits cube files to collapse
        out_dir : str
            Output dirname for new created file with the result of the collapse
        mean : bool, optional
            If trun, the collapse use the mean value instead of the arithmetic sum.
        start: int, optional
            First plane of the cube to use for the collapse, default 0
        end: int, optional
            Last plane (included) of the cube to use for the collapse, default -1, means 
            the last plane.
            Examples: 
              - if we want to collapse the first two planes (0 and 1), we should
              say start=0, end=1
              - if we want to collapse only the first plane (not really a collapse),
              we should say start=0, end=0


        Returns
        -------
        Return a list with the new collapsed frames. If no collapse is required, file
        will be created as well.
    """

    log.debug("Starting collapse() method ....")
    
    new_frame_list = [] 
    n = 0

    if not frame_list or len(frame_list) == 0 or not frame_list[0]:
        return []

    for frame_i in frame_list:
        f = fits.open(frame_i)
        if mean:
            t_filename = out_dir + "/" + os.path.basename(frame_i).replace(".fits", "_avg.fits")
        else:
            t_filename = out_dir + "/" + os.path.basename(frame_i).replace(".fits", "_coadd.fits")
        
        # First, we need to check if we have MEF files
        if len(f) > 1 and len(f[1].data.shape) == 3:
            try:
                log.info("Collapsing a MEF cube %s" % frame_i)
                out = collapse_mef_cube(frame_i, t_filename, mean, start, end)
                new_frame_list.append(out)
            except Exception as e:
                log.error("Some error collapsing MEF cube: %s" % str(e))
                f.close()
                raise e
        elif len(f) > 1 and len(f[1].data.shape)==2:
            log.debug("MEF file has no cubes, no collapse required.")
            # shutil.copyfile(frame_i, t_filename)
            new_frame_list.append(frame_i)
        elif len(f[0].data.shape) != 3:  # 2D !
            log.debug("It is not a FITS-cube image, no collapse required")
            # shutil.copyfile(frame_i, t_filename)
            new_frame_list.append(frame_i)
        else:            
            # Suppose we have single CUBE file with N planes
            out_hdulist = fits.HDUList()
            if mean:
                log.debug("Averaging data cube...from %s to %s" %(start, end))
                if end != -1:
                    prihdu = fits.PrimaryHDU(data = f[0].data[start:end + 1, :, :].mean(0), header=f[0].header)
                else:
                    # up to the last plane
                    prihdu = fits.PrimaryHDU(data = f[0].data[start:, :, :].mean(0), header=f[0].header)
            else:
                log.debug("Adding data cube...from %s to %s" %(start, end))
                if end != -1:               
                    prihdu = fits.PrimaryHDU(data=f[0].data[start:end + 1, :, :].sum(0), header=f[0].header)
                else:
                    prihdu = fits.PrimaryHDU(data=f[0].data[start:, :, :].sum(0), header=f[0].header)

            prihdu.scale('float32') 
            # Updating PRIMARY header keywords...
            prihdu.header.set('NCOADDS', f[0].data.shape[0])
            if mean:
                prihdu.header.set('EXPTIME', f[0].header['EXPTIME'])
            else:
                prihdu.header.set('EXPTIME', f[0].header['EXPTIME'] * f[0].data.shape[0])                
            prihdu.header.set('PAPIVERS', __version__, "PANIC Pipeline version")
            # Weird case (OmegaCass), but it produce a fail with WCS lib
            if 'CTYPE3' in prihdu.header:
                prihdu.header.remove("CTYPE3")
            if 'CRPIX3' in prihdu.header:
                prihdu.header.remove("CRPIX3")
            if 'CRVAL3' in prihdu.header:
                prihdu.header.remove("CRVAL3")
            if 'CDELT3' in prihdu.header:
                prihdu.header.remove("CDELT3")
            
            out_hdulist.append(prihdu)    
            # out_hdulist.verify ('ignore')
            # Now, write the new collapsed file
            out_hdulist.writeto(t_filename, output_verify='ignore',
                                 overwrite=True)
            
            out_hdulist.close(output_verify='ignore')
            del out_hdulist
            new_frame_list.append(t_filename)
            log.info("FITS file %s created" % (new_frame_list[n]))
            n += 1
        # always
        f.close()
     
    return new_frame_list


def collapse_mef_cube(inputfile, out_filename=None, mean=False, start=0, end=-1):
    """
    Collapse each of the extensions of a MEF file
    """

    f = fits.open(inputfile)

    out_hdulist = fits.HDUList()
    prihdu = fits.PrimaryHDU (data = None, header = f[0].header)
    prihdu.header.set('NCOADDS', f[1].data.shape[0])
    if mean:
        prihdu.header.set('EXPTIME', f[0].header['EXPTIME'])
    else:
        prihdu.header.set('EXPTIME', f[0].header['EXPTIME']*f[1].data.shape[0])
    prihdu.header.set('PAPIVERS', __version__, "PANIC Pipeline version")
    out_hdulist.append(prihdu)    
 
    # Sum each extension
    for ext in range(1,len(f)):
        if mean:
            log.debug("Averaging MEF data cube...from %s to %s" %(start, end))
            if end !=-1:
                hdu = fits.ImageHDU(data=numpy.float32(f[ext].data[start:end + 1, :, :].mean(0)),
                            header=f[ext].header)
            else:
                hdu = fits.ImageHDU(data=numpy.float32(f[ext].data[start:, :, :].mean(0)),
                            header=f[ext].header)
        else:
            log.debug("Adding MEF data cube...from %s to %s" %(start, end))
            if end !=-1:
                hdu = fits.ImageHDU(data=numpy.float32(f[ext].data[start:end + 1, :, :].sum(0)),
                            header=f[ext].header)
            else:
                hdu = fits.ImageHDU(data=numpy.float32(f[ext].data[start:, :, :].sum(0)),
                            header=f[ext].header)
        #hdu.scale('float32') --> bug con astropy 1.3 !!! 
        out_hdulist.append(hdu)    
    
    # Now, write the new collapsed file
    if out_filename is None:
        if mean:
            outfile = inputfile.replace(".fits", "_avg_%s.fits" % str(f[1].data.shape[0]).zfill(3))
        else:
            outfile = inputfile.replace(".fits", "_coadd_%s.fits" % str(f[1].data.shape[0]).zfill(3))
    else:
        outfile = out_filename 
    out_hdulist.writeto(outfile, output_verify='ignore', overwrite=True)
        
    out_hdulist.close(output_verify='ignore')
    del out_hdulist
    log.info("FITS file %s created" % (outfile))

    return outfile

def collapse_distinguish(frame_list, out_filename="/tmp/collapsed.fits"):
    """
    Collapse (sum) a set of distinguish files (not cubes) into a single 2D image.

    Return the name of the output file created.
    
    Curretly not used from PAPI, **only** from command-line.
    """

    log.debug("Starting collapse_distinguish() method ....")
    
    new_frame_list = [] 
    if frame_list is None or len(frame_list) == 0 or frame_list[0] is None:
        return []

    for frame_i in frame_list:
        f = fits.open(frame_i)
        # First, we need to check if we have MEF files
        if len(f)>1 and len(f[1].data.shape)==3:
            log.error("MEF-cubes files cannot be collapsed. First need to be split !")
            raise Exception("MEF-cubes files cannot be collapsed. First need to be split !")
        elif len(f)>1 and len(f[1].data.shape)==2:
            log.error("Not implemented yet.")
            raise Exception("MEF-2D files cannot be collapsed. Not implemented yet.")
            ## TO BE COMPLETED !!! ##
            log.debug("Found a MEF with a 2D-image: %s:" % frame_i)
            new_frame_list.append(frame_i)
            if len(new_frame_list)==1:
                sum = numpy.zeros(len(f)-1, [f[1].header['NAXIS1'], 
                                   f[1].header['NAXIS2']], dtype='float32')
                header1 = f[0].header
            for i in range(len(f)):
                sum[i] += f[i+1].data
        elif len(f)==1 and len(f[0].data.shape)==2:
            log.debug("Found a 2D-image: %s:"%frame_i)
            new_frame_list.append(frame_i)
            if len(new_frame_list)==1:
                sum = numpy.zeros([f[0].header['NAXIS1'], 
                                   f[0].header['NAXIS2']], dtype='float32')
                header1 = f[0].header
            sum += f[0].data
            f.close()
        
    # Now, save the collapsed set of files in a new single file        
    out_hdulist = fits.HDUList()
                   
    prihdu = fits.PrimaryHDU (data = sum, header = header1)
    #prihdu.scale('float32') bug con astropy 1.3 !!! 
        
    # Updating PRIMARY header keywords...
    prihdu.header.set('NCOADDS', len(new_frame_list))
    prihdu.header.set('EXPTIME', header1['EXPTIME']*len(new_frame_list))
    prihdu.header.set('PAPIVERS', __version__, "PANIC Pipeline version")
    
    out_hdulist.append(prihdu)    
    #out_hdulist.verify ('ignore')
    # Now, write the new single FITS file
    out_hdulist.writeto(out_filename, output_verify='ignore', overwrite=True)
    
    out_hdulist.close(output_verify='ignore')
    del out_hdulist
    log.info("FITS file %s created" % (out_filename))
     
    return out_filename


def create_cube(frame_list, out_filename="/tmp/cube.fits"):
    """
    Create a cube (not sum) from a set of individual files (not cubes).

    Return the name of the output file (cube) created.
    
    Curretly not used from PAPI, **only** from command-line.

    """

    log.debug("Starting create_cube() method ....")
    
    new_frame_list = [] 
    if frame_list is None or len(frame_list) == 0 or frame_list[0] is None:
        return []

    for frame_i in frame_list:
        f = fits.open(frame_i)
        # First, we need to check if we have MEF files
        if len(f) > 1 and len(f[1].data.shape) == 3:
            log.error("MEF-cubes files cannot be converted to cubes. First need to be split !")
            raise Exception("MEF-cubes files cannot be converted to cubes. First need to be split !")
        elif len(f)>1 and len(f[1].data.shape)==2:
            log.error("Not implemented yet.")
            raise Exception("MEF-2D files cannot be converted to a cube. Not implemented yet.")
        elif len(f)==1 and len(f[0].data.shape)==2:
            log.debug("Found a 2D-image: %s:" % frame_i)
            new_frame_list.append(frame_i)
            if len(new_frame_list) == 1:
                i = 0
                # First image
                cube = numpy.zeros((len(frame_list), 
                                    f[0].header['NAXIS1'], 
                                    f[0].header['NAXIS2']), 
                                    dtype=f[0].data.dtype)
                header1 = f[0].header
            cube[i,:,:] = f[0].data[:,:]
            i += 1
        f.close()
        
    # Now, save the collapsed set of files in a new single file        
    out_hdulist = fits.HDUList()
                   
    prihdu = fits.PrimaryHDU (data = cube, header = header1)
    #prihdu.scale('float32') bug con astropy 1.3 !!! 
        
    # Updating PRIMARY header keywords...
    prihdu.header.set('NAXIS3', len(new_frame_list))
    # prihdu.header.set('EXPTIME', header1['EXPTIME']*len(new_frame_list))
    prihdu.header.set('PAPIVERS', __version__, "PANIC Pipeline version")
    
    out_hdulist.append(prihdu)    
    #out_hdulist.verify ('ignore')
    # Now, write the new single FITS file
    out_hdulist.writeto(out_filename, output_verify='ignore', overwrite=True)
    
    out_hdulist.close(output_verify='ignore')
    del out_hdulist
    log.info("FITS CUBE file %s created" % (out_filename))
     
    return out_filename

    
################################################################################
# main
################################################################################
def main(arguments=None):

    log.info("Start-of-collapse")

    # Get and check command-line options
        
    desc = "Collapse (add them up arithmetically) each cube of a list files into a single 2D image."

    parser = argparse.ArgumentParser(description=desc)
    
    parser.add_argument("-i", "--input_image",
                  action="store", dest="input_image", 
                  help="input FITS cube image (MEF or non MEF) to collapse into a 2D coadded image")
    
    parser.add_argument("-L", "--input_image_list",
                  action="store", dest="input_image_list", 
                  help="input list of FITS (MEF or non MEF) to be collapsed individually into a 2D coadded image")
    
    parser.add_argument("-l", "--input_single_image_list",
                  action="store", dest="input_single_image_list", 
                  help="input image list (text file) of a set of single images (non MEF) to be collapsed (or cubed) into a single 2D coadded image")

    parser.add_argument("-o", "--output_file",
                  action="store", dest="output_file", 
                  help="output filename (default = %(default)s)",
                  default="/tmp/out.fits")

    parser.add_argument("-d", "--output_dir",
                  action="store", dest="output_dir", 
                  help="output directory (default = %(default)s)",
                  default="/tmp")

    parser.add_argument("-M", "--mean",
                  action="store_true", dest="mean", default=False,
                  help="Compute the Average of the cube instead of the Sum [default=%(default)s]")

    parser.add_argument("-c", "--cube",
                  action="store_true", dest="cube", default=False,
                  help="Build a cube from the image list of individual files (input_single_image_list) [default=%(default)s]")

    parser.add_argument("-s", "--start",
                  action="store", dest="start", default=0, type=int,
                  help="First plane to use for the collapse [default=%(default)s]")
    
    parser.add_argument("-e", "--end",
                  action="store", dest="end", default=-1, type=int,
                  help="Last plane (included) to use for the collapse [default=%(default)s]")


    options = parser.parse_args()
    
    if len(sys.argv[1:]) < 1:
       parser.print_help()
       sys.exit(0)

    if (not options.input_image and not options.input_image_list and
            not options.input_single_image_list):
        # args is the leftover positional arguments after all options have been processed
        parser.print_help()
        parser.error("Wrong number of arguments " )
    
    if options.input_image and options.input_single_image_list:
        # only one option can be executed 
        parser.print_help()
        parser.error("Only one option can be used")
        
    if options.input_image:
        if not os.path.exists(options.input_image):
            log.error("Input image %s does not exist", options.input_image)
            sys.exit(0)
        if not options.output_dir or not os.path.exists(options.output_dir):
            parser.print_help()
            parser.error("Wrong number of arguments " )

        try:
            frames = [options.input_image]
            print(collapse(frames, options.output_dir, options.mean, options.start, options.end))
        except Exception as e:
            log.info("Some error while collapsing image to 2D: %s" % str(e))
            sys.exit(0)
    
    elif options.input_image_list:
        if not os.path.exists(options.input_image_list):
            log.error("Input file %s does not exist", options.input_image_list)
            sys.exit(0)
        if not options.output_dir or not os.path.exists(options.output_dir):
            parser.print_help()
            parser.error("Wrong number of arguments ")

        try:
            frames = [line.replace("\n", "") for line in 
                      fileinput.input(options.input_image_list)]
            print(collapse(frames, options.output_dir, options.mean, options.start, options.end))
        except Exception as e:
            log.info("Some error while collapsing images: %s" % str(e))
            sys.exit(0)
            
    elif options.input_single_image_list:
        try:
            if options.mean:
                log.error("Sorry, mean option is not implemented yet for this mode!")
                sys.exit(0)

            frames = [line.replace("\n", "") for line in 
                      fileinput.input(options.input_single_image_list)]
            if options.cube:
                create_cube(frames, options.output_file)
            else:
                collapse_distinguish(frames, options.output_file)
        except Exception as e:
            log.info("Some error while collapsing set of images to single image: %s" % str(e))
            sys.exit(0)
        
    log.info("End-of-collapse")

######################################################################
if __name__ == "__main__":
    sys.exit(main())
