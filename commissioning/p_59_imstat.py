#!/usr/bin/env python
#########################################################################
# PANIC data with H4RG
#########################################################################
# Imstat PANIC data
# Inputs:
# - FITS file cube
# 
# usage: p_59_imstat.py [-h] [--nolog]
#                                      
# 1.0 31/01/2024 JM Creation 

_name = 'p_59_imstat.py'
_version = '1.0'

#########################################################################

#!/usr/bin/env python
################################################################################
#
#
# PAPI (PANIC PIpeline)
#
# modFITS.py
#
# Modify some keyword value
#
# Created    : 25/11/2010    jmiguel@iaa.es -
# Last update: 28/05/2013    jmiguel@iaa.es - 
#             Adapted to work with old version of PyFITS (i.e., arch.osn.iaa.es)
#              17/09/2013    jmiguel@iaa.es
#                            New name and now keywords can be added.
#              09/10/2019    Moved to Python3
# TODO
#     - Give a map of keyword-value as input
################################################################################

################################################################################
# Import necessary modules

import fileinput
import argparse
import sys

# Interact with FITS files
import astropy.io.fits as fits
import numpy as np


def imstatFITS(files):
	"""
	Method used compute stats of a list of FITS files.
	
	Parameters
	----------
	files: sequence 
		A list FITS files
        
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
			nexps = 1
			cdscube = np.zeros((4096, 4096, nexps)).astype('int32')
			data = np.rollaxis(hdulist[0].data.astype('int32'), 0, 3)			
			header = hdulist[0].header
			rmode = 'cntsr'
			if rmode == 'cntsr':
				cpar1 = header['CPAR1'] # cycle type parameter (number of frames per exp)
				m_filter = header['FILTER']
				m_itime = header['ITIME']
				for iexp in range(nexps):
					# CDS from multiple frame cubes
					# cdsdata = data[:, :, 1] - data[:, :, 0]
					cdscube[:, :, iexp] = (data[:, :, cpar1*iexp + cpar1 -1] - data[:,:, cpar1*iexp])
					cds_median = np.median(cdscube[:, :, iexp])
					median_last_frame = np.median(data[:, :, cpar1*iexp + cpar1 -1])
					median_reset_frame = np.median(data[:,:, cpar1*iexp])
					print('Filter: %s' %m_filter)
					print('Itime: %s' %m_itime)
					print('Median last frame = %f' %median_last_frame)
					print('Median reset frame = %f' %median_reset_frame)
					print('Frame diff  = %f' %(median_last_frame - median_reset_frame))
					print('CDS Median = %f' %cds_median)	
			else:
				# rrr and lir (cpar=2)
				for iexp in range(nexps):
					# CDS from multiple frame cubes
					# cdsdata = data[:, :, 1] - data[:, :, 0]
					cdscube[:, :, iexp] = (data[:, :, 2*iexp + 1] - data[:,:, 2*iexp])
		
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
    desc = "FITS imstat tool"
    parser = argparse.ArgumentParser(description=desc)
    
    parser.add_argument("-f", "--fits",
                  action="store", dest="fits", type=str,
                  help="Input FITS file. It has to be a fullpath file name")
    
    parser.add_argument("-l", "--input",
                  action="store", dest="input_file_list", type=str,
                  help="Source file list of data frames. It has to be a fullpath file name")
                  
    
    options = parser.parse_args()
    
    if options.fits:
        filelist = [options.fits]
    elif options.input_file_list:
        filelist = [line.replace( "\n", "") for line in fileinput.input(options.input_file_list)]
    else:
        parser.print_help()
        parser.error("incorrect number of arguments ")
            
    try:
        imstatFITS(filelist)    
    except Exception as e:
        raise e

######################################################################
if __name__ == "__main__":
    sys.exit(main())
