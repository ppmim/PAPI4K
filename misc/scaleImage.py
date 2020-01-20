#!/usr/bin/env python

""""
module for FITS image escale
"""

import os
import argparse
import sys

from astropy.io import fits
from astLib import *
import logging
import glob


TEST_IMAGE = "/home/jmiguel/.mcs/003h14b8.fit"
TEST_IMAGE = "/home/jmiguel/DATA/OSN/GJ480-0003V_2.fit"
TEST_IMAGE = "/home/jmiguel/DATA/o2k/20120105/o2k-20120106-02:30:31-sci-ferm.fits"

def scale_image(filename, scale_factor):

    if not os.path.exists(filename):
        print("File %s does no exists" % filename)
        return

    try:
        img = fits.open(filename)
        wcs = astWCS.WCS(filename)
        d = img[0].data
    except Exception as e:
        logging.error("Cannot open file: %s" % str(e))
        raise e

    outfilename = os.path.basename(filename).replace(".fits", "_scaled.fits")

    try:
        scaled = astImages.scaleImage(d, wcs, float(scale_factor))
        astImages.saveFITS(outfilename, scaled['data'], scaled['wcs'])
    except Exception as ex:
        logging.error("Error scaling image: %s" %str(ex))
        raise
    else:
        logging.info("Image scaled: %s" % outfilename)

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', dest='file',
                        help='name of file')

    parser.add_argument('-d', '--directory', dest='dir',
                        help='directory to look for FITS files to scale')

    parser.add_argument('-s', '--scale', dest='scale',
                        help='scale factor for image scaling [0-5]')

    args = parser.parse_args()
    if not args.scale:
        parser.print_usage()
        sys.exit(0)

    if args.dir:
        files = glob.glob(args.dir + "/*.fits")
    elif args.file:
        files = [args.file]
    else:
        parser.print_usage()
        sys.exit(0)

    for file in files:
        try:
            logging.info("Scaling image: %s" % file)
            scale_image(file, args.scale)
        except Exception as ex:
            logging.error(ex)
        else:
            logging.info("Ending")

