#! /usr/bin/env python

""" 
    Run Get the unique values of [read_mode, itime, ncoadd, save_mode]
    for the files of a given directory.
"""

# Author: Jose M. Ibanez (c) 2014
# Email: jmiguel@iaa.es
# License: GNU GPLv3

import argparse
import sys
import os
import shutil
import glob
import fileinput
import astropy.io.fits as fits

def parse_ranges(input_string):
    """
    # Example usage
    input_string = '[1024:3071,1024:3071]'
    result = parse_ranges(input_string)
    """
    
    # Remove the square brackets and split by the comma
    cleaned_string = input_string.strip('[]')
    ranges = cleaned_string.split(',')

    # Parse each range into start and end values
    parsed_ranges = []
    for r in ranges:
        start, end = map(int, r.split(':'))
        parsed_ranges.append((start, end))
    
    return parsed_ranges


def getItimesNcoadds(path, output_file, recursive=False):
    """
    Read all the FITS file of the given path and create a 
    output_file with a table with the unique combinations
    of [read_mode, itime, ncoadds, save_mode].
    
    - DARK and DOME_LAMP_[ON|OFF] images are ignored.
    - Only lir and rrr-mpia images are recognized.
    - Cubes (SEF or MEF) are detected and the number of layers is used as NCOADDS.
    
    Example of output file:
    
    lir       2.7   2  mef   1  4096  1 4096
    lir       5.0  10  mef   1  4096  1 4096
    rrr-mpia  1.3   5  mef   1024   2048  1024  2048
    rrr-mpia  1.3   5  sef   1024   2048  1024  2048
    
    
    """
    
    # Read the files
    if os.path.exists(path):
        if os.path.isfile(path):
            try:
                hdulist = fits.open(path)
                filelist = [path]
            except:
                filelist = [line.replace("\n", "")
                            for line in fileinput.input(path)]
        elif os.path.isdir(path):
            filelist = glob.glob(path + "/*.fit*")
            # Look for subdirectories
            if recursive:
                subdirectories = [ name for name in os.listdir(path) \
                    if os.path.isdir(os.path.join(path, name)) ]
                for subdir in subdirectories:
                    filelist += glob.glob(os.path.join(path, subdir)+"/*.fit*")
    else:
        print("Error, file %s does not exits" % path)
        return 0
     
    file_types = []
    # output pathname
    home = os.path.expanduser("~")
    tmp_dir = os.getenv("TMPDIR")
    
    if tmp_dir==None or not os.path.isdir(tmp_dir):
        msg = "TMPDIR directory %s not found. Using %s directory\n"
        sys.stderr.write(msg % (tmp_dir, home ))
        full_output_file = home + "/" + output_file
    else:
        full_output_file = tmp_dir + "/" + output_file

    fd = open(full_output_file + "_tmp_", "w+")
    fd.write("# READMODE\tITIME\tNCOADDS\tSAVEMODE\tX\tXRANGE\tY\tYRANGE\n")
     
    for my_file in filelist:
        try:
            my_fits = fits.open(my_file, mode='readonly', memmap=True, do_not_scale_image_data=True, ignore_blank=True,
                                       ignore_missing_end=False, lazy_load_hdus=True)
            # Image type
            if 'IMAGETYP' in  my_fits[0].header:
                papitype = my_fits[0].header['IMAGETYP']
            else:
                papitype = 'unknown'
                
            # Ignore DARKs and DOME_LAMP_[ON|OFF] images
            if "DARK" in papitype  or "LAMP" in papitype:
                print("Image is a DARK or DOME_LAMP_. Skipping file %s" % my_file)
                continue
            
            # Read-Mode
            read_mode = my_fits[0].header['READMODE']

            if read_mode == 'line.interlaced.read': 
                read_mode = 'lir'
            elif read_mode == 'fast-reset-read.read':
                read_mode = 'rrr-mpia'
            elif read_mode == 'continuous.sampling.read':
                read_mode = 'cntsr'
            elif read_mode == 'fast-reset.read':
                read_mode = 'rr-mpia'
            elif read_mode == 'o2.single.corr.read':
                read_mode = 'o2scr'
            elif read_mode == 'reset.level.read':
                read_mode = 'rlr'
            elif read_mode == 'reset.read.read':
                read_mode = 'rrr'
            elif read_mode == 'o2.double.corr.read':
                read_mode = 'o2dcr'
            elif read_mode == 'fast.end-corr-dcr.read':
                read_mode = 'fecr'    
            else:
                print("Read mode [%s] not recognized. Skipping file %s" %(read_mode,my_file))
                continue
            
            # ITIME
            itime = my_fits[0].header['ITIME']
            
            # Save mode
            if len(my_fits) > 1:
                save_mode = 'mef'
            else:
                save_mode = 'sef'
            
            # NCOADDS: if we have a cube, we take into account the number of layers
            if save_mode == 'mef' and len(my_fits[1].data.shape) > 2:
                ncoadds = my_fits[1].data.shape[0]
            elif save_mode == 'sef' and len(my_fits[0].data.shape) > 2:
                #ncoadds = my_fits[0].data.shape[0]
                ncoadds = my_fits[0].header['NEXP']
            else:
                #ncoadds = my_fits[0].header['NCOADDS']
                ncoadds = my_fits[0].header['NEXP']
            
            # Subwin
            # DETSEC  = '[1024:3071,1024:3071]' / [pix] xrange and yrange of window
            # DETSIZE = '[1:4096,1:4096]'    / [px] full size of the detector
            detsec =  my_fits[0].header['DETSEC']
            p =  parse_ranges(detsec)
            x, xrange = (p[0][0]), (p[0][1]-p[0][0] + 1)
            y, yrange = (p[1][0]), (p[1][1]-p[1][0] + 1)


            # Finaly, write out the parameters to text file
            if [read_mode, itime, ncoadds, save_mode, x, xrange, y, yrange] not in file_types:
                file_types.append([read_mode, itime, ncoadds, save_mode, x, xrange, y, yrange])
                # Insert into output file
                fd.write("%s\t\t%3.03f\t%d\t%s\t\t%d\t%d\t%d\t%d\n"%(read_mode, float(itime), int(ncoadds), save_mode, x, xrange, y, yrange))
        except Exception as e:
            print("Error while reading file: %s\n %s"%(my_file,str(e)))

    fd.close()
    shutil.move(full_output_file + "_tmp_", full_output_file)
    print("Output file %s written" % full_output_file)
    
    return len(file_types)
    

if __name__ == "__main__":

    
    usage = "usage: %prog [options] "
    desc = """Get the unique values of [read_mode, itime, ncoadd, save_mode]
for the files of a given directory to know the DARKs required for them."""

    parser = argparse.ArgumentParser(description=desc)
    
                  
    parser.add_argument("-s", "--source",
                  action="store", dest="source_file",
                  help="Source directory or txt file listing the filenames of input images to read.")
    
    parser.add_argument("-o", "--output_file",
                  action="store", dest="output_file", default="filetypes.txt",
                  help="Output file to be generated [default: %(default)s]")
    
    parser.add_argument("-r", "--recursive",
                  action="store_true", dest="recursive", default=False,
                  help="Recursive subdirectories if source is a directory name (only first level)")
    
    options = parser.parse_args()
    
    if len(sys.argv[1:]) < 1:
        parser.print_help()
        sys.exit(0)

    if not options.source_file or not options.output_file:
        parser.print_help()
        parser.error("incorrent number of arguments")
    
    try:    
        n = getItimesNcoadds(options.source_file, options.output_file)
    except Exception as ex:
        print("Error reading FITS files: %s" %str(ex))

    print("%d types found !" % n)
    
    sys.exit()
