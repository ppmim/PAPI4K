import numpy as np
import matplotlib.pyplot as plt

from astropy.io import fits
from astropy.utils.data import get_pkg_data_filename
from astropy.convolution import Gaussian2DKernel, interpolate_replace_nans
from astropy.convolution.kernels import CustomKernel

from scipy.signal import convolve as scipy_convolve

import sys
from optparse import OptionParser


def apply_low_pass_filter(filename, mask, output_filename):

    
    hdu = fits.open(filename)[0]
    
    # This example is intended to demonstrate how astropy.convolve and
    # scipy.convolve handle missing data, so we start by setting the brightest
    # pixels to NaN to simulate a "saturated" data set
    # img[img > 2e1] = np.nan
    img = hdu.data

    # We smooth with a Gaussian kernel with x_stddev=1 (and y_stddev=1)
    # It is a 9x9 array
    #kernel = Gaussian2DKernel(x_stddev=1, x_size=3, y_size=3)

    array = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]])
    custom_kernel = CustomKernel(array)

    # Spread the NaNs (3x3) with a custom kernel
    fixed_image = scipy_convolve(img, custom_kernel, mode='same', method='direct')


    kernel = Gaussian2DKernel(x_stddev=1)

    # create a "fixed" image with NaNs replaced by interpolated values
    fixed_image = interpolate_replace_nans(fixed_image, kernel)

    
    # Now we do a bunch of plots.  In the first two plots, the originally masked
    # values are marked with red X's
    plt.figure(1, figsize=(12, 6)).clf()
    plt.close(2) # close the second plot from above

    ax1 = plt.subplot(1, 2, 1)
    im = ax1.imshow(img, vmin=-2., vmax=2.e1, origin='lower',
                    interpolation='nearest', cmap='viridis')
    y, x = np.where(np.isnan(img))
    ax1.set_autoscale_on(False)
    ax1.plot(x, y, 'rx', markersize=4)
    ax1.set_title("Original")
    ax1.set_xticklabels([])
    ax1.set_yticklabels([])

    ax2 = plt.subplot(1, 2, 2)
    im = ax2.imshow(fixed_image, vmin=-2., vmax=2.e1, origin='lower',
                    interpolation='nearest', cmap='viridis')
    ax2.set_title("Fixed")
    ax2.set_xticklabels([])
    ax2.set_yticklabels([])


    # Save new file
    fits.writeto(output_filename,
                 fixed_image, header=hdu.header, overwrite=True)    



if __name__ == "__main__":

    usage = "usage: %prog [options]"
    desc = """Apply low pass filter to image to remove bad pixels"""
    
    parser = OptionParser(usage, description=desc)
    
    parser.add_option("-s", "--source", type="str",
                  action="store", dest="source_filename",
                  help="Source image to clean.")
    
    parser.add_option("-m", "--mask", type="str",
                  action="store", dest="mask_file",
                  help="Mask file of pixels to be cleaned (0=good, 1=bad pixeles)")
        
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
    
    
    if options.mask_file:
        mask = options.mask_file
    else:
        mask = None

    try:
        apply_low_pass_filter(options.source_filename, 
                       mask, 
                       options.output_filename)
    except Exception as e:
        log.error("Error cleaning image. %s " % str(e))
        
    sys.exit(0)