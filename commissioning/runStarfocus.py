#! /usr/bin/env python

""" Run IRAF.starfocus, get the best Focus for a focus sequence. """

# Author: Jose M. Ibanez (c) 2015
# Email: jmiguel@iaa.es
# License: GNU GPLv3

import os
import re
import argparse
import sys
import fileinput
import locale
from os.path import expanduser

# To avoid conflict with QL-Focus_Evaluation
try:
    if os.path.exists(expanduser("~") + "/iraf/focus_seq.txt"):
        os.unlink(expanduser("~") + "/iraf/focus_seq.txt")
        print("Deleted file ~/iraf/focus_seq.txt")
except Exception as e:
    print("Error, cannot delete ~/iraf/focus_seq.txt")

    
from astropy.io import fits
import numpy as np
import matplotlib
# Next is needed in order to avoid a crash/deadlock when running 
# pyraf graphs and matplotlib.pyplot graphs
# For 'TkAgg' backend (default) produces the crash.
matplotlib.use('QT5Agg')

import matplotlib.pyplot as plt
from pyraf import iraf
import papi.misc.display as display

# Global variable !
telescope = ""


def getBestFocusfromStarfocus(images, coord_file, log_file):
    """
    Calculate the average Full Width Half Max for the objects in image
    at the coords specified in coord_file calling iraf.obsutil.psfmeasure,
    interactively or non-interactively if coord_file is given.

    Paramaters
    ----------
    images: str
        Filename of the file listing the files to be analyzed. It must start
        with '@' for iraf formatting.
        
    coord_file: str
        Filename of the file with the coordinages (x, y) of the stars to be
        analyzed by iraf.starfocus.
        If coord_file == "", then the routine will lauch ds9 and the user must
        select the stars for the focus evaluation.
    
    log_file: str
        Filename of the log file where iraf.starfocus will write the results.
       

    The coordinates in coord_file should be in the same world coordiantes
    as the WCS applied to the image.
    
    Exam. coord_file:
    1024  1024
    
    
    Returns
    -------
    The best focus obtained by iraf.starfocus.
    
    
    """
    
    locale.setlocale(locale.LC_ALL, '')
    locale.setlocale(locale.LC_NUMERIC, 'C')

    global telescope

    # Read NCOADDS of the images to set the SATURATION limit
    if os.path.isfile(images[1:]):
        files = [line.replace("\n", "").replace('//', '/')
                     for line in fileinput.input(images[1:])]
        with fits.open(files[0]) as hdu:
            if 'NCOADDS' in hdu[0].header:
                satur_level = hdu[0].header['NCOADDS'] * 50000
            else:
                satur_level = 50000
            if 'TELESCOP' in hdu[0].header:
                telescope = hdu[0].header['TELESCOP']
            else:
                telescope = ""
    else:
        msg = "Error, cannot find file %s" %(images[1:])
        print(msg)
        raise Exception(msg)
    
    print("SATUR_LEVEL =", satur_level)
    
    if coord_file == "" or not coord_file:
        idisplay = "yes"
    else: 
        idisplay = "no"
        if not os.path.isfile(coord_file):
            msg = "ERROR, cannot open file %s" % coord_file
            raise Exception(msg)
    
    print("IDISPLAY=", idisplay)
    print("COORD_FILE=", coord_file)
    print("IMAGES_FILE", images)
    import stsci.tools.capable
    print("OF_GRAPHICS=", stsci.tools.capable.OF_GRAPHICS)
    print("LC_NUMERIC =", locale.getlocale(locale.LC_NUMERIC))
    
    if 'IMTDEV' in os.environ:
        print("IMTDEV=", os.environ['IMTDEV'])
    
    if 'PYRAF_NO_DISPLAY' in os.environ:
        print("DEBUG -- PYRAF_NO_DISPLAY=", os.environ['PYRAF_NO_DISPLAY'])
    if 'PYTOOLS_NO_DISPLAY' in os.environ:
        print("DEBUG -- PYTOOLS_NO_DISPLAY=", os.environ['PYTOOLS_NO_DISPLAY'])
    
    print("LOG_FILE=", log_file)
        
    # Be sure the logfile is writtable
    try:
        with open(log_file, "w") as f:
            pass
    except IOError as e:
        print("Could not open log file: %s" % log_file)
        raise e
                  
    # Config and launch the iraf.starfocus task (if coord_file, then non-interactive)
    try:
        iraf.noao(_doprint=0)
        iraf.obsutil(_doprint=0)
        iraf.unlearn("starfocus")
      
        starfocus = iraf.obsutil.starfocus
        starfocus.focus = "T_FOCUS"
        starfocus.fstep = "" 
        starfocus.nexposures = 1 
        starfocus.coords = "mark1"
        starfocus.wcs = "physical" 
        starfocus.size = "MFWHM"
        # Usually the value starfocus.scale = 1 to measure sizes in pixels or if starfocus.scale = 'image pixel scale value' 
        # in arc seconds per pixel
        starfocus.scale = 1
        starfocus.radius = 10
        starfocus.sbuffer = 10 
        starfocus.swidth= 10
        starfocus.saturation = satur_level
        # starfocus.saturation = "INDEF"
        starfocus.ignore_sat = "no"
        starfocus.imagecur = coord_file
        starfocus.display = idisplay
        starfocus.frame = 1
        starfocus.graphcur = "" #"/dev/null" 
        starfocus.logfile = log_file
        res = starfocus(images, Stdout=1)[-1]   # get last linet of output
        numMatch = re.compile(r'(\d+(\.\d+)?)')
        match = numMatch.search(res)
        
        best_focus = float(match.group(1))
        print("\n\nBest Focus (IRAF)= ", best_focus)
        return best_focus
    
    except Exception as e:
        print("Error running IRAF.starfocus: %s" % str(e))
        raise e

def writeDataFile(best_focus, min_fwhm, avg_x, avg_y, 
                      data_file, target):
    """
    Write a data file to be used
    later for the Tilt analysis (p_50_tiltcheck.py).
    """
    
    if data_file:
        fo = open(data_file, 'w')
        if target:
            obj = target
        else:
            print('WARNING: Object name not provided')
            obj = 'Unknowm'
        fo.write('# Object: %s\n' %obj)
        line = " Average best focus of %f with FWHM of %f\n" % (best_focus, min_fwhm)
        fo.write('#%s' % line)
        line = "  Best focus estimate @ (%f, %f): FWHM=%f, m=0.0, f=%f\n" % \
               (avg_x, avg_y, min_fwhm, best_focus)
        fo.write(line)
        fo.close()
        print('Data file written: %s' % data_file)
    else:
        print('Error, no data file given')


def find_last_occurrence_and_get_lines(file_path, search_string):
    last_occurrence_line = None
    lines_below_occurrence = []

    with open(file_path, 'r') as file:
        lines = file.readlines()

    for line_num, line in enumerate(reversed(lines), start=1):
        if search_string in line:
            last_occurrence_line = len(lines) - line_num + 1
            lines_below_occurrence = lines[last_occurrence_line:]
            break

    return last_occurrence_line, lines_below_occurrence


def readStarfocusLog(log_file):
    """
    Read the results from the iraf.starfocus log file and compute
    the best focus for that execution. Only non-saturated data
    are read.
    """
    
    # Read the last lines 
    # with open(log_file, "r") as f:
    #     f.seek(0, 2)                    # Seek @ EOF
    #     fsize = f.tell()                # Get Size
    #     f.seek(max(fsize-2**15, 0), 0)  # Set pos @ last chars
    #     lines = f.readlines()           # Read to end
    
    # lines.reverse()
    # my_lines = []
    
    # # Look for the last execution (It must start with
    # # 'NOAO/IRAF') 
    # while not lines[0].strip().startswith('NOAO/IRAF'):
    #     my_lines.append(lines[0])
    #     lines.pop(0)

    # my_lines.reverse()

    last_occ, my_lines = find_last_occurrence_and_get_lines(log_file, 'NOAO/IRAF')

    data = []
    # start to read the right columns
    for line in my_lines:
        if line.strip().startswith('Image'):
            # Heading line
            continue
        elif line.strip().startswith('Best'):
            # End reading
            break
        elif line.strip().startswith('Average'):
            # End reading
            break
        elif line.strip().startswith('Focus'):
            # End reading
            break
        elif len(line.split()) == 0: 
            # Blank line
            continue
        else:
            # Read columns, only non-saturated data
            if line.split()[-1] != '*':
                if line.split()[0].startswith("/"):
                    data.append(line.split()[1:9])
                else:
                    data.append(line.split()[0:8])
     
    return data


def getBestFocus(data, output_file):
    """
    Fit the input data read from starfocus log file,
    to a parabola and find out the minimun (best focus estimation).
    
    Parameters
    ----------
    data: list
        A list with N rows x M (8) columns with the next correspondence:
        Column    Line     Mag   Focus   MFWHM Beta   Ellip      PA  
        
    output_file: str
        Filename of out plot with the fitting computed.
        
    Returns
    -------
    If success, returns the best focus computed in mm, and min FWHM in pixels.
    
    """
    
    if telescope == 'CA-2.2':
        foclimits = [-1, 27]
        pix_scale = 0.375
        print("Assuming CA-2.2 TELESCOPE")
    elif telescope == 'CA-3.5':
        foclimits = [10, 60]
        pix_scale = 0.192
        print("Assuming CA-3.5 TELESCOPE")
    else:
        print("Asumming CA-2.2 TELESCOPE")
        foclimits = [-1, 27]
        pix_scale = 0.375
        
    d = np.array(data, dtype=np.float32)
    good_focus_values = d[:, 3] # focus
    
    # The FWHM units are adjusted by the pixel scale factor; 
    # Usually the value starfocus.scale = 1 to measure sizes in pixels or if starfocus.scale = 'image pixel scale value' 
    # in arc seconds per pixel
    fwhm_values = d[:, 4] # PSF-value (MFWHM, GFWHM, FWHM, ...)
    

    print("\n---------")
    print("N_POINTS: ", len(fwhm_values))
    print("----------\n")
    
    m_foc = good_focus_values.mean()
    good_focus_values = good_focus_values - m_foc
    try:
        z = np.polyfit(good_focus_values, fwhm_values, 2)
        print("Fit = %s  \n" % str(z))
        # Note that poly1d returns polynomials coefficients, in increasing powers !
        pol = np.poly1d(z)
    except Exception as ex:
        print("Error computing best focus. Maybe due to wrong data in starfocus.log: %s"%str(ex))
        sys.exit(0)
        
    xp = np.linspace(np.min(good_focus_values ) - 0.5, 
                     np.max(good_focus_values ) + 0.5, 500) # number or points to interpolate

    # best focus is derivative of parabola = 0
    # but check if it is correctly curved
    if pol[2] < 0:
        print("ERROR: Parabola fit unusable!")
    best_focus = - pol[1] / (2. * pol[2])
    min_fwhm = pol([best_focus])
    print("BEST_FOCUS (OWN) = ", best_focus + m_foc)
    print("MIN_FWHM (OWN) = ", min_fwhm)
    
    if foclimits and (best_focus + m_foc < foclimits[0] or best_focus + m_foc > foclimits[1]):
        print("ERROR: Best focus out of range!")
        best_focus_out_of_range = True
    else:
        best_focus_out_of_range = False
    
    # Write best focus for OT
    writeValueForOT(best_focus + m_foc)
    
    # Plotting
    plt.plot(good_focus_values + m_foc, fwhm_values, '.')
    plt.plot(xp + m_foc, pol(xp), '-')
    plt.axvline(best_focus + m_foc, ls='--', c='r')
    plt.title("Best Focus=%6.3f mm - FWHM=%6.3f pix / %2.2f arcsec"
        %((best_focus + m_foc), min_fwhm , min_fwhm * pix_scale))
    
    plt.xlabel("T-FOCUS (mm)")
    plt.ylabel("FWHM (pixels)") # startfocus.scale = 1
    plt.xlim(np.min(good_focus_values + m_foc) - 0.1, np.max(good_focus_values + m_foc) + 0.1)
    plt.ylim(np.min(fwhm_values) - 1, np.max(fwhm_values) + 1 )
    if pol[2] < 0:
        plt.figtext(0.5, 0.5, 'ERROR: Parabola fit unusable!', size='x-large', color='r', weight='bold', ha='center', va='bottom')
    if best_focus_out_of_range:
        plt.figtext(0.5, 0.5, 'ERROR: Best focus out of range!', size='x-large', color='r', weight='bold', ha='center', va='top')
    plt.grid()
    
    
    plt.savefig(output_file)
    
    print('Image saved: ', output_file)
    show = True
    if show:
        plt.show(block=True)
    
    # Print out Values
    # for idx, foc_value in enumerate(good_focus_values):
    #    sys.stdout.write("\nFoc. value: %s   -->  FWHM: %s"%(foc_value, fwhm_values[idx]))
    
    return (best_focus + m_foc), min_fwhm


def runFocusEvaluation(source_file, coord_file, log_file):
    """
    Run the complete procedure for focus evaluation.
    """
    
    # First, check if ds9 is launched; if not, launch it.
    if not os.path.exists(coord_file):
        display.startDisplay()
        
    if not os.path.exists(source_file):
        msg = "ERROR, file source_file does not exists"
        print(msg)
        raise Exception(msg)
    
    try:
        best_focus = getBestFocusfromStarfocus("@" + source_file, 
                                           coord_file, 
                                           log_file)
    
    except Exception as e:
        raise e
    
    # Compute our own BEST_FOCUS value and plot the fittting
    print("Now, our own fitting...\n")
    home = expanduser("~")
    try:
        data = readStarfocusLog(home + "/iraf/starfocus.log")
        my_best_focus, min_fwhm  = getBestFocus(data, "starfocus.pdf")
    except Exception as ex:
        print("Error while computing best focus: %s" % str(ex))
    

def writeValueForOT(best_focus):
    """
    Write the value into text file (~/tmp/ql_focus) for OT
    
    Paramaters
    ----------
    best_focus: float (mm)
    
    Returns
    -------
    Filename written.
    
    """

    home = expanduser("~")
    tmp_dir = os.getenv("TMPDIR")
        
    if tmp_dir==None or not os.path.isdir(tmp_dir):
        msg = "tmp directory %s not found. Using %s directory\n"
        sys.stderr.write(msg % (tmp_dir, home ))
        ql_focus_text_file = home + "/ql_focus"
    else:
        ql_focus_text_file = tmp_dir + "/ql_focus"

    with open(ql_focus_text_file, "w") as text_file:
        # best_focus [microns] are written to
        # text file ready to be read and used by OT.
        text_file.write("%d" % int(round(best_focus*1000)))
    
    return ql_focus_text_file


##############################################################################
def main(arguments=None):
    
    desc = """Run IRAF.starfocus for a focus sequecen and return the best focus"""

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("-s", "--source",
                  action="store", dest="source_file",
                  help="Source file listing the filenames of input images.")
    
    parser.add_argument("-c", "--coordiantes",
                  action="store", dest="coord_file",
                  help="Coordinates file listing the x,y coordiantes "
                  "of stars in input images")
    
    parser.add_argument("-o", "--output_log",
                  action="store", dest="log_file", default="starfocus.log", 
                  help="Output log file generated [default: %(default)s]")
    
    parser.add_argument("-d", "--data_file",
                  action="store", dest="data_file",
                  help="Output data file for analysis")
    
    parser.add_argument("-t", "--target",
                  action="store", dest="target",
                  help="Object name for output data")

    options = parser.parse_args()
    
    if len(sys.argv[1:]) < 1:
       parser.print_help()
       sys.exit(0)
       
    # Wrong number of args
    if not options.source_file and not options.coord_file and not options.log_file:
        parser.print_help()
        parser.error("incorrent number of arguments")

    #########
    # QL-call
    #########
    # only read current log and compute BestFocus (used from QL, called from
    # papi_ql_user.cl)
    elif not options.source_file and not options.coord_file and options.log_file:
        data = readStarfocusLog(options.log_file)
        my_best_focus, min_fwhm = getBestFocus(data, "starfocus.pdf")

    ########################
    # USER-Full-interactive
    # ######################
    # run iraf.starfocus and compute our own BestFocus
    elif options.source_file and options.coord_file and not options.data_file:
        try:
            bf = runFocusEvaluation(options.source_file, 
                                    options.coord_file,
                                    options.log_file)
        except Exception as e:
            print("ERROR running focus evaluation")
            raise e

    #######################
    # USER-non-interactive (based on coord_file)
    #######################
    # Complete execution (used for Tilt Analysis)
    else:
        # display.startDisplay()
        # Run iraf.starfocus
        best_focus = getBestFocusfromStarfocus("@" + options.source_file, 
                                               options.coord_file,
                                               options.log_file)
        
        # Compute our own BEST_FOCUS value and plot the fittting
        print("Now, our own fitting...\n")
        data = readStarfocusLog(options.log_file)
        
        plot_filename = os.path.splitext(options.data_file)[0] + ".pdf"
        my_best_focus, min_fwhm = getBestFocus(data, plot_filename)
        
        d = np.array(data, dtype=np.float32)
        avg_x = d[:, 0].mean()
        avg_y = d[:, 1].mean()
        # Write values into data file for the Tilt analysis.
        writeDataFile(my_best_focus, min_fwhm, avg_x, avg_y, 
                      options.data_file, options.target)

        iraf_data_file = options.data_file.replace(".txt", "_iraf.txt")
        writeDataFile(best_focus, min_fwhm, avg_x, avg_y, 
                      iraf_data_file, options.target)
        
    sys.exit(0)

######################################################################
if __name__ == "__main__":
    sys.exit(main())
