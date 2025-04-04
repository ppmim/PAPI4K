#! /usr/bin/env python
#encoding:UTF-8

# Copyright (c) 2015 Jose M. Ibanez All rights reserved.
# Institute of Astrophysics of Andalusia, IAA-CSIC
#
# This file is part of PAPI
#
# PAPI is free software: you can redistribute it and/or modify
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


import math
import sys
import os
import logging as log
import fileinput
import argparse


import numpy
import astropy.io.fits as fits

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from papi.datahandler.clfits import ClFits
# To be able to run in any common python environment without Qt
matplotlib.use('TkAgg')


def draw_offsets_H2RG(offsets, pix_scale = 0.45, scale_factor=1.0):

    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111, aspect='equal')
    max_x = numpy.abs(offsets[: , 0]).max()
    max_y = numpy.abs(offsets[: , 1]).max()
    detector_id = 1
    # The width of the rectangle simulate the full detector with the gap (4096x4096 + 167) 
    r_width = (4096 + 167) / 1.0 * pix_scale * scale_factor
    plt.xlim(offsets[: , 0].min() - (4096 + 167) / 2.0 * pix_scale - 100, offsets[: , 0].max() + (4096 + 167) / 2.0 * pix_scale + 100)
    plt.ylim(offsets[: , 1].min() - (4096 + 167) / 2.0 * pix_scale - 100, offsets[: , 1].max() + (4096 + 167) / 2.0 * pix_scale + 100)
    plt.xlabel("RA (arcsec)")
    plt.ylabel("Dec (arcsec)")
    plt.title("Ditther offsets (magnification = %02.1f, pix_scale = %02.2f)" % (scale_factor, pix_scale))
    plt.grid()
    
    # To align offsets with sky-orientation
    offsets = offsets * (-1)
    print("offsets =", offsets)
    offsets_q1 = [1024 + 84, -(1024 + 84)]
    offsets_q2 = [1024 + 84, 1024 + 84]
    offsets_q3 = [-(1024 + 84), 1024 + 84]
    offsets_q4 = [-(1024 + 84), -(1024 + 84)]
    
    q_offsets = [offsets_q1, offsets_q2, offsets_q3, offsets_q4]
    q_offsets = numpy.asarray(q_offsets) * pix_scale * scale_factor
    
    q_width = 2048 * pix_scale * scale_factor
    
    for o in q_offsets:
        # Draw offsets for quadrant/detector-i
        for x,y in (offsets + o):
            print("X=%s , Y=%s" % (x, y))
            ax2.add_patch(
                patches.Rectangle(
                    (x - q_width / 2.0, y - q_width / 2.0),
                    q_width,
                    q_width,
                    fill=True, alpha=0.3  # remove background
                )
            )
            ax2.annotate('%s'%detector_id, xy=(x,y), xytext=(x,y), size=8)
        detector_id+=1
        
    plt.show(block=True)
    fig2.savefig('offsets.png', dpi=360, bbox_inches='tight')


def draw_offsets_H4RG(offsets, pix_scale = 0.375, scale_factor=1.0):

    # To align offsets with sky-orientation
    offsets[:, 1] = offsets[:, 1] * (-1)
    # offsets = offsets * (-1)
    print("offsets =", offsets)

    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111, aspect='equal')
    max_x = numpy.abs(offsets[: , 0]).max()
    max_y = numpy.abs(offsets[: , 1]).max()

    # The width of the rectangle simulate the full detector (4096 x 4096) 
    r_width = 4096 / 1.0 * pix_scale * scale_factor
    plt.xlim(offsets[: , 0].min() - (4096) / 2.0 * pix_scale - 100, offsets[: , 0].max() + (4096) / 2.0 * pix_scale + 100)
    plt.ylim(offsets[: , 1].min() - (4096) / 2.0 * pix_scale - 100, offsets[: , 1].max() + (4096) / 2.0 * pix_scale + 100)
    plt.xlabel("RA (arcsec)")
    plt.ylabel("Dec (arcsec)")
    plt.title("Ditther offsets (magnification = %02.1f, pix_scale = %02.2f)" % (scale_factor, pix_scale))
    plt.grid()
    
    # To align offsets with sky-orientation
    # offsets = offsets * (-1)
    # offsets[:, 0] = offsets[:, 0] * (-1)
    
    q_width = 4096 * pix_scale * scale_factor
    
    # Draw offsets for detector
    step = 0
    for x,y in offsets:
        print("STEP=%d, X=%s , Y=%s" % (step, x, y))
        ax2.add_patch(
            patches.Rectangle(
                (x - q_width / 2.0, y - q_width / 2.0),
                q_width,
                q_width,
                fill=True, alpha=0.3  # remove background
            )
        )
        ax2.annotate('%s'%step, xy=(x,y), xytext=(x,y), size=8)
        step +=1
        
    #plt.show(block=True)
    fig2.savefig('offsets.png', dpi=360, bbox_inches='tight')

def getWCSPointingOffsets(images_in,
                              p_offsets_file="/tmp/offsets.txt"):
      """
      Derive pointing offsets of each image taking as reference the first one and
      using WCS astrometric calibration of the images. Note that is **very** 
      important that the images are astrometrically calibrated.
      
        Parameters
        ----------
                
        images_in: str
            list of filename of images astrometrically calibrated
        p_offsets_file: str
            filename of file where offset will be saved (it can be used
            later by dithercubemean). The format of the file will be:
            
            /path/to/filename00   offsetX00   offsetY00
            /path/to/filename01   offsetX01   offsetY01
            ...
            /path/to/filename0N   offsetX0N   offsetY0N
            
        Returns
        -------    
        offsets: narray          
                two dimensional array (Nx2) with offsets (in pixles),
                where N=number of files.
                
        Notes:
            It assumed that the input images have a good enough astrometric
            calibration (hopefully obtained with Astrometry.net), and North
            is up and East is left, and no rotation angle exists.
            
        
      """
      
      log.info("Starting getWCSPointingOffsets....")

      
      # Very important the pixel scale in order to find out good offsets values !!
      pix_scale = 0.375 # arcsec/px @ T2.2m; 0.192 @ T3.5m
      # Init variables
      i = 0 
      offsets_mat = None
      ra0 = -1
      dec0 = -1
      offsets = numpy.zeros([len(images_in), 2] , dtype=numpy.float32)
      
      # First, we must sort out the files by MJD
      dataset = []
      sorted_files = []
      for ifile in images_in:
        try:
            mjd = fits.getval(ifile, "MJD-OBS", ext=0)
        except KeyError:
            try:
                mjd = fits.getval(ifile, "JD", ext=0)
            except KeyError:
                raise Exception("Cannot find neither MJD-OBS nor JD")
        dataset.append((ifile, mjd))
      # Sort out the files
      dataset = sorted(dataset, key=lambda data_file: data_file[1])
      # Created sorted list
      for l_tuple in dataset:
        sorted_files.append(l_tuple[0])
      
      print("SORTED", sorted_files)
      
      # Reference image
      ref_image = sorted_files[0]
      try:
            ref = ClFits(ref_image)
            # If present, pix_scale in header is prefered
            pix_scale = 0.375 # ref.pixScale
            print("-->PIXSCALE = ", pix_scale)
            ra0 = ref.ra    
            dec0 = ref.dec
            log.debug("Ref. image: %s RA0= %s DEC0= %s PIXSCALE= %f" % (ref_image, ra0, dec0, pix_scale))
      except Exception as e:
          log.error("Cannot get reference RA_0, Dec_0 coordinates: %s" % str(e))
          raise e
        
      offset_txt_file = open(p_offsets_file, "w")
      for my_image in sorted_files:
            try:
                ref = ClFits(my_image)
                ra = ref.ra
                dec = ref.dec
                log.debug("Image: %s RA[%d]= %s DEC[%d]= %s"%(my_image, i, ra, i, dec))
                
                # Assummed that North is up and East is left
                # To give the results in arcsec, set pix_scale=1.0
                pix_scale = 1
                # In order to recover the original offsets given into the Observing Tool (OT),
                # refered as offset at DEC=0 (equator), we need to take into account the cos(DEC)
                # and undo the DEC correction.
                diff_ra =  ra - ra0
                if diff_ra < 0: diff_ra = diff_ra + 360
                elif diff_ra > 360: diff_ra = diff_ra - 36  

                offsets[i][0] = ((ra - ra0)*3600 * math.cos(dec/57.29578)) / float(pix_scale)
                offsets[i][1] = ((dec0 - dec)*3600) / float(pix_scale)
                
                log.debug("offset_ra  = %s" % offsets[i][0])
                log.debug("offset_dec = %s" % offsets[i][1])
                
                offset_txt_file.write(my_image + "   " + "%.6f   %0.6f\n"%(offsets[i][0], offsets[i][1]))
                i+=1
            except Exception as e:
                log.error("Error computing the offsets for image %s. \n %s"%(my_image, str(e)))
                raise e
            
      offset_txt_file.close()
      
      # Write out offsets to file
      # numpy.savetxt(p_offsets_file, offsets, fmt='%.6f')
      log.debug("(WCS) -> Image Offsets (arcsecs): ")
      log.debug(offsets)
      
      # Some stats
      print("MEAN_X=", numpy.mean(offsets[:,0]))
      print("STD_X=", numpy.std(offsets[:,0]))
      print("RMS_X", numpy.sqrt(numpy.mean(numpy.absolute(offsets[:,0][2])**2)))

      print("MEAN_Y=", numpy.mean(offsets[:, 1]))
      print("STD_Y=", numpy.std(offsets[:, 1]))
      print("RMS_Y", numpy.sqrt(numpy.mean(numpy.absolute(offsets[:, 1])**2)))
      
      return offsets
  

#################
# MAIN #
#################
if __name__ == "__main__":
    
    usage = "usage: %prog [options]"
    desc = """Gives the image offsets (arcsecs) based on the WCS of the image headers.""" 
    """ A plot of the dither pattern is also saved as offsets.png"""

    parser = argparse.ArgumentParser(description=desc)

    
    parser.add_argument("-s", "--source", type=str,
                  action="store", dest="source_file",
                  help="Input text file with the list of FITS file to be analized.")
                  
    parser.add_argument("-o", "--output", type=str,
                  action="store", dest="output_filename", default="offsets.txt",
                  help="Output file to write the offset matrix")
    
    parser.add_argument("-p", "--pix_scale", type=float,
                  action="store", dest="pix_scale", default=0.375,
                  help="Pixel scale [default=%(default)s]")
    
    parser.add_argument("-d", "--draw_scale", type=float,
                  action="store", dest="draw_scale", default=1.0,
                  help="Draw scale of detector (0.0-1.0) [default=%(default)s]")

    options = parser.parse_args()
    
    if len(sys.argv[1:]) < 1:
       parser.print_help()
       sys.exit(0)
        
    # args is the leftover positional arguments after all options have been processed 
    if not options.source_file or not options.output_filename: 
        parser.print_help()
        parser.error("incorrect number of arguments " )
        
    
    if os.path.isfile(options.source_file):
        files = [line.replace("\n", "").replace('//','/')
            for line in fileinput.input(options.source_file)]
    else:
        print("Error, cannot read file : ", options.source_file)
        sys.exit(0)
    
    # Try to get PIX_SCALE
    with fits.open(files[0], mode="readonly") as hdu:
        if 'PIXSCALE' in hdu[0].header:
            pix_scale = hdu[0].header['PIXSCALE']
        else:
            pix_scale = options.pix_scale

        if 'CAMERA' in hdu[0].header:
            if 'H2RG' in hdu[0].header['CAMERA']:
                is_H2RG = True
            else:
                # lets suppose is a monolithic detector (ie.: H4RG)
                is_H2RG = False
        else:
            is_H2RG = False

            
    try:    
        offsets = getWCSPointingOffsets(files, options.output_filename)
    except Exception as e:
        log.error("Error, cannot find out the image offsets. %s",str(e))
    
    # Draw plot with dither pathern
    if is_H2RG:
        draw_offsets_H2RG(offsets, pix_scale, options.draw_scale)
    else:
        draw_offsets_H4RG(offsets, pix_scale, options.draw_scale)

    
    # Print out the offset matrix
    numpy.set_printoptions(suppress=True)
    print("\nOffsets Matrix (arcsecs): \n")
    print(offsets)
    
    sys.exit(0)

