#! /usr/bin/env python

#########################################################################
# PANIC data with H4RG
#########################################################################
# Convert Raw
# Inputs:
# - FITS file cube
# 
# usage: p_59_imstat.py [-h] [--nolog]
#                                      
# 1.0 31/01/2024 JM Creation 

_name = 'convRaw2CDS.py'
_version = '1.0'

#########################################################################

#!/usr/bin/env python
################################################################################
#
#
# PAPI (PANIC PIpeline)
#
# convRaw2CDS
#
# Convert CNTSR raw FITS files (reset + exposition frames) to CDS image
# CDS: correlated double sample data, what is computed subtracting reset frame to
# last frame of the single frame cube.
#
# Created    : 20/02/2024    jmiguel@iaa.es -
# TODO: implement combination of NEXP into a single expos
################################################################################

################################################################################
# Import necessary modules

import fileinput
import argparse
import sys
import os

# Interact with FITS files
import astropy.io.fits as fits
import numpy as np


def convRaw2CDS(files, out_dir, suffix):
	"""
	Method used convert Single frame cubes (raw data) to
	CDS data and compute stats of a list of FITS files.
	
	Parameters
	----------
	files: sequence 
		A list FITS files
	out_dir: string
		Output directory for created CDS files
	suffix: string
		suffix to add to the new created FITS files

	Returns
	-------
	Number of files read    
	"""

	print("Starting imstatFITS...")

	for file in files:      
		try:
			# To preserve image scale (BITPIX)--> do_not_scale_image_data 
			# (http://goo.gl/zYkc6)
			# Other option, is use fits.ImageHDU.scale_back
			hdulist = fits.open(file, mode="readonly", do_not_scale_image_data=False)
		except IOError:
			print('Error, can not open file %s' % (file))
			continue

		# Check if it is a MEF file
		if len(hdulist) > 1:
			print("[Error] Wrong Extension number for file: %s" % file)
			continue

		try:
			new_fits = fits.PrimaryHDU()
			new_fits.header = hdulist[0].header.copy()
			data = np.rollaxis(hdulist[0].data.astype('int32'), 0, 3)
			header = hdulist[0].header
			cpar1 = header['CPAR1'] # cycle type parameter (number of frames per exp)
			nexps = header['NEXP'] # crep (number of repetitions)
			cdscube = np.zeros((4096, 4096, nexps)).astype('int32')
			print("NEXP = %02i" %nexps)
			rmode = 'cntsr'
			if rmode == 'cntsr':
				for iexp in range(nexps):
					print("IEXP=%02i"%iexp)
					# CDS from multiple frame cubes
					# cdsdata = data[:, :, 1] - data[:, :, 0]
					cdscube[:, :, iexp] = (data[:, :, cpar1*iexp + cpar1 -1] - data[:,:, cpar1*iexp])
					cds_median = np.median(cdscube[:, :, iexp])
					median_last_frame = np.median(data[:, :, cpar1*iexp + cpar1 -1])
					median_reset_frame = np.median(data[:,:, cpar1*iexp])
					std_reset_frame = np.std(data[:,:, cpar1*iexp])
					new_fits.data = cdscube[:, :, iexp].astype('float32')
					new_fits.header['BZERO'] = 0
					new_fits.header['BSCALE'] = 1
					new_fits.header['HISTORY'] = 'CNTSR: raw single cube CONVERTED to CDS'
					new_hdulist = fits.HDUList([new_fits])
					# Compose output filename
					mfnp = os.path.basename(file).partition('.fits')
					# add suffix before .fits extension, or at the end if no such extension present
					outfitsname = out_dir + '/' + mfnp[0] + suffix + "_%04i"%(iexp+1) + mfnp[1] + mfnp[2]
					outfitsname = os.path.normpath(outfitsname)
					# outfitsname = file.replace(".fits", "_%s.fits"%suffix)
					new_hdulist.writeto(outfitsname, overwrite=True)
					print('FITS file created: %s' % outfitsname)
					print('Median last frame = %f' %median_last_frame)
					print('Median reset frame = %f' %median_reset_frame)
					print('STD reset frame = %f' %std_reset_frame)
					print('Frame diff  = %f' %(median_last_frame - median_reset_frame))
					print('CDS Median = %f' %cds_median)

				combine = True
				combine_sum = True
				combine_median = False
				if combine_median or combine_sum:
					if combine_median:
						# Apply sigma clipping to the cube
						sigma = 3.0
						print('Sigma clipping...')
						clipped_cube = sigma_clip(cdscube, sigma=sigma, maxiters=2, axis=2)
						# Calculate the median along the axis (axis=2)
						# shortcut if nothing is clipped
						if clipped_cube.count() == clipped_cube.size:
							pr('No data clipped')
							median_image = np.median(cdscube, axis=2)
						else:
							median_image = np.ma.median(cdscube, axis=2).filled(np.nan)

					elif combine_sum:
						median_image = cdscube.sum(2)

					# create and save fits file
					new_fits.data = median_image.astype('float32')
					new_fits.header['BZERO'] = 0
					new_fits.header['BSCALE'] = 1
					new_fits.header['NCOADDS'] = nexps
					new_hdulist = fits.HDUList([new_fits])
					if combine_median:
						outfitsname = out_dir + '/' + mfnp[0] + suffix + "_median" + mfnp[1] + mfnp[2]
						new_fits.header['HISTORY'] = 'CDS and median average sigclip'
					else:
						outfitsname = out_dir + '/' + mfnp[0] + suffix + "_coadd" + mfnp[1] + mfnp[2]
						new_fits.header['HISTORY'] = 'CDS and coadd of NEXPs'

					outfitsname = os.path.normpath(outfitsname)
					print('    - Saving output file %s' %outfitsname)
					new_hdulist.writeto(outfitsname, overwrite=True)

				del cdscube

		except Exception as e:
			print("[Error] Cannot run stats of file %s: \n %s"%(file, str(e)))
			hdulist.close()
    
	print("End of imstatFITS")
	return
    
def nowtime():
	return datetime.datetime.now().isoformat()

def pr(msg):
	'''Print messages and write to log file'''
	print(msg)
	if writelog:
		logfile = open(os.path.join(outputpath, 'Logfile.txt'), 'a')
		logfile.write(msg + '\n')
		logfile.close()

################################################################################
# main
def main(arguments=None):
    
    # Get and check command-line options
    desc = "FITS RAW to CDS conversion"
    parser = argparse.ArgumentParser(description=desc)
    
    parser.add_argument("-f", "--fits",
                  action="store", dest="fits", type=str,
                  help="Input FITS file. It has to be a fullpath file name")
    
    parser.add_argument("-l", "--input",
                  action="store", dest="input_file_list", type=str,
                  help="Source file list of data frames. It has to be a fullpath file name")
                  
    parser.add_argument("-o", "--out_dir", type=str, dest="out_dir",
                  action="store", default="/tmp",
                  help="filename of out data file (default: %(default)s)")

    parser.add_argument("-S", "--suffix", type=str,
                  action="store", dest="suffix", default="_CDS",
                  help="Suffix to use for new corrected files (default: %(default)s)")

    options = parser.parse_args()
    
    if options.fits:
        filelist = [options.fits]
    elif options.input_file_list:
        filelist = [line.replace( "\n", "") for line in fileinput.input(options.input_file_list)]
    else:
        parser.print_help()
        parser.error("incorrect number of arguments ")
            
    try:
        convRaw2CDS(filelist, options.out_dir, options.suffix)
    except Exception as e:
        raise e

######################################################################
if __name__ == "__main__":
    sys.exit(main())
