#!/usr/bin/env python

# Copyright (c) 2015 IAA-CSIC  - All rights reserved. 
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


from __future__ import (absolute_import, division,
                        unicode_literals)
import numpy as np
from astropy import log
import astropy.io.fits as fits
import sys
from optparse import OptionParser


def _clean_masked_pixels(data, mask, size=5, exclude_mask=None):
    """
    Clean masked pixels in an image.  Each masked pixel is replaced by
    the median of unmasked pixels in a 2D window of ``size`` centered on
    it.  If all pixels in the window are masked, then the window is
    increased in size until unmasked pixels are found.

    Pixels in ``exclude_mask`` are not cleaned, but they are excluded
    when calculating the local median.
    
    Parameters
    ----------
    data: the image array to clean 
    
    mask: an array that is True (or >0) where image contains bad pixels
    
    size: int
        size of the centered 2D window
    
    exclude_mask: an array mask that is True (or >0) where pixeles
    are not cleaned, and excluded when calculating the local median.
    
    Returns
    -------
    
    The cleaned arraray image.
    
    """

    assert size % 2 == 1, 'size must be an odd integer'
    assert data.shape == mask.shape, \
        'mask must have the same shape as image'
    ny, nx = data.shape
    
    mask_coords = np.argwhere(mask)
    #mask_coords = np.argwhere(mask==0)
    
    if exclude_mask is not None:
        assert data.shape == exclude_mask.shape, \
            'exclude_mask must have the same shape as data'
        maskall = np.logical_or(mask, exclude_mask)
    else:
        maskall = mask
        
    mask_idx = maskall.nonzero()
    #mask_idx = (maskall==0)
    data_nanmask = data.copy()
    data_nanmask[mask_idx] = np.nan
    print("Number of BPs = %d" % np.isnan(data_nanmask).sum())

    nexpanded = 0
    for coord in mask_coords:
        y, x = coord
        median_val, expanded = _local_median(data_nanmask, x, y, nx, ny,
                                             size=size)
        data[y, x] = median_val
        if expanded:
            nexpanded += 1
    if nexpanded > 0:
        log.info('    Found {0} {1}x{1} masked regions while '
                 'cleaning.'.format(nexpanded, size))
    return data


def _local_median(data_nanmask, x, y, nx, ny, size=5, expanded=False):
    """
    Compute the local median in a 2D window, excluding NaN.
    
    Note: min number of goodpixel is 1; should it be increased ?
    """
    
    hy, hx = size // 2, size // 2
    x0, x1 = np.array([x - hx, x + hx + 1]).clip(0, nx)
    y0, y1 = np.array([y - hy, y + hy + 1]).clip(0, ny)
    region = data_nanmask[y0:y1, x0:x1].ravel()
    goodpixels = region[np.isfinite(region)]
    if len(goodpixels) > 0:
        median_val = np.median(goodpixels)
    else:
        newsize = size + 2     # keep size odd
        median_val, expanded = _local_median(data_nanmask, x, y, nx, ny,
                                             size=newsize, expanded=True)
    return median_val, expanded

def test( im, mask ):
    """
    Other way to clean Bad Pixels, however it's extremely slow !!!
    and not sure if it works fine...
    LOOP over images pixels is forbiden in python !!!!
    
    """
    from scipy import interpolate, ndimage
    
    # Convert gainmap to binary mask (1=badpixels, 0=goodpixels)
    mask = np.where(mask == 0, 1, 0)
    
    # create domains around masked pixels
    dilated = ndimage.binary_dilation(mask)
    domains, n = ndimage.label(dilated)

    # loop through each domain, replace bad pixels with the average
    # from nearest neigboors
    y, x = np.indices(im.shape, dtype=np.int)[-2:]
    #x = xarray(im.shape)
    #y = yarray(im.shape)
    cleaned = im.copy()
    print("N=", n)
    for d in (np.arange(n) + 1):
        print("iter =", d)
        # find the current domain
        i = (domains == d)

        print("step 1")
        # extract the sub-image
        x0, x1 = x[i].min(), x[i].max() + 1
        y0, y1 = y[i].min(), y[i].max() + 1
        subim = im[y0:y1, x0:x1]
        submask = mask[y0:y1, x0:x1]
        subgood = (submask == False)
        print("step 2")

        cleaned[i * mask] = subim[subgood].mean()
        print("X0= %f X1= %f , Y0= %f Y1= %f" % (x0, x1, y0, y1))

    return cleaned

def cleanBadPixels( input_image, bpm, output_file=None, is_gainmap=False):
    
    input_data, input_header = fits.getdata(input_image, header=True)
    input_mask = fits.getdata(bpm, header=False)

    # Special case of gainmap, where bad pixels are = 0 (no gain)
    if is_gainmap:
        input_mask = np.where(input_mask == 0, 1, 0)
    
    new_data = _clean_masked_pixels(input_data, input_mask)
    # new_data = test(input_data, input_mask)
    
    # Write cleaned data
    if output_file == None:
        output_file = input_image.replace(".fits", "_clean.fits")
    
    fits.writeto(output_file,
                 new_data, header=input_header, clobber=True)
    
    return output_file



def bad_pixel_fix(image,hdr,sizex,sizey,newfilename,s=3):
    ''' Fixes bad pixels by interpolating from surrounding pixels.
        Copied from:
        http://mtham.ucolick.org/egates/2016GradWorkshop/PDFs/DataReduction/DataReductionProcedures-Python-2016.pdf
        Inputs:
            image (2d array): image to be fixed
            hdr (fits header): header of image for getting
            sizex, sizey (float): dimensions of image to be fixed
            newfilename (str): new file name
            s (int): radius of pixels to use in interpolation (default = 3)
        Returns:
            flat_div (2d array): pixel corrected image
    '''

    # Depending on the size of the image, load the correct bad pixel list:
    #     (Python indicies are (row,column) so the image indicies are (y,x) in python; additionally python begins with
    #      initial index of 0, while image data begins at 1)
    if sizex == 1024 and sizey == 1024:
        badpix = np.loadtxt(open("nirc2.1024.1024.badpix","rb"))
        badpix = badpix.astype(int)
    elif sizex == 512 and sizey == 512:
        badpix = np.loadtxt(open("nirc2.512.512.badpix","rb"))
        badpix = badpix.astype(int)
    else:
        print("I don't have a bad pixel list to match this image size.  I only have 1024x1024 or 512x512.  \
        Check your image sizes please.")
        return None

    # Make a boolean mask the same size as the image and set all initial values to False:
    mask = np.ma.make_mask(image,copy=True,shrink=True, dtype=np.bool)
    mask[:,:] = False
    # For each bad pixel in the list, set the value of the mask to true:
    for i in badpix:
        mask[i[1]-1][i[0]-1] = True
    # Set the value of all bad pixels in the image to nan:
    mdata = np.ma.masked_array(image,mask=mask,fill_value=np.nan)
    # Make a new array as a copy of original image:
    badpixelfixed = image.copy()
    # For each x and y value, loop through image and replace the value of all "nan"
    # pixels with the mean of the four pixels on either side of the bad one:
    for i in range(0,mdata.shape[0]):
        for j in range(0,mdata.shape[1]):
            if np.math.isnan(mdata[i,j]):
                x1 = i-s
                x2 = i+s+1
                y1 = j-s
                y2 = j+s+1
                if x1<0:
                    x1 = 0
                if x2>mdata.shape[0]:
                    x2=mdata.shape[0]
                if y1<0:
                    y1 = 0
                if y2>mdata.shape[1]:
                    y2 = mdata.shape[1]
                badpixelfixed[i,j] = np.mean(mdata[x1:x2,y1:y2])
    # Add a comment to the header:
    hdr['COMMENT'] = '         Bad pixels fixed on '+time.strftime("%m/%d/%Y")+ ' By Logan A. Pearce'
    # Write out the bad pixel corrected image to a new fits file:
    fits.writeto(newfilename,badpixelfixed,hdr,overwrite=True)
    return badpixelfixed
    
    


if __name__ == "__main__":

    usage = "usage: %prog [options]"
    desc = """Clean masked (bad) pixels from an input image. Each masked pixel 
is replaced by the median of unmasked pixels in a 2D window of ``size`` centered on
it.  If all pixels in the window are masked, then the window is
increased in size until unmasked pixels are found."""
    
    parser = OptionParser(usage, description=desc)
    
    parser.add_option("-s", "--source", type="str",
                  action="store", dest="source_filename",
                  help="Source image to clean.")
    
    parser.add_option("-m", "--mask", type="str",
                  action="store", dest="mask_file",
                  help="Mask file of pixels to be cleaned (0=good, 1=bad pixeles)")
    
    parser.add_option("-g", "--gainmap", type="str",
                  action="store", dest="gainmap",
                  help="Gainmap (instead of MASK_FILE) of pixels to be cleaned (0>good pixels, 1=bad pixeles)")
    
    parser.add_option("-o", "--output", type="str",
                  action="store", dest="output_filename", 
                  help="Output file to write the clean image.")
    
    (options, args) = parser.parse_args()
    
    if len(sys.argv[1:]) < 1:
       parser.print_help()
       sys.exit(0)
        
    # args is the leftover positional arguments after all options have
    # been processed
    if not options.source_filename or len(args) != 0: 
        parser.print_help()
        parser.error("incorrect number of arguments ")
    
    if options.mask_file and options.gainmap:
        parser.print_help()
        parser.error("Only one kind of mask can be provided")
   
    if options.gainmap:
        mask = options.gainmap
    else:
        mask = options.mask_file
    try:
        cleanBadPixels(options.source_filename, 
                       mask, 
                       options.output_filename,
                       is_gainmap = False)
    except Exception as e:
        log.error("Error cleaning image. %s " % str(e))
        
    sys.exit(0)
    