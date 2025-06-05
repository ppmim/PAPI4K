#!/usr/bin/env python

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


################################################################################
#########################################################################
# PANIC data processing
#########################################################################
# Example of nonlinearity correction for full frame MEF files
# Includes many sanity checks, the actual calculation is very simple
# Incorrectable and saturated pixels are set to NaN. Therefore the ouptut
# data is float.
#
# 1.0 14/07/2014 BD Creation (correct_nonlinearity.py)
#
# 1.1 18/07/2014 JMIM Adaption to PAPI (correctNonLinearity.py)
# 
# 1.2 08/02/2024 JMIM Update to new PANIC detector H4RG

_name = 'correctNonLinearity.py'
_version = '1.2'
################################################################################
# Import necessary modules
import numpy as np
import astropy.io.fits as fits
import dateutil.parser
import sys
import os
import fileinput
import argparse
import multiprocessing


# PAPI modules
from papi.misc.mef import MEF
from papi.misc.paLog import log
from papi.misc.version import __version__

# If you want to use the new multiprocessing module in Python 2.6 within a class, 
# you might run into some problems. Here's a trick how to do a work-around. 
def unwrap_self_applyModel(arg, **kwarg):
    return NonLinearityCorrection.applyModel(*arg, **kwarg)


class NonLinearityCorrection(object):
    """
    Class used to correct the Non-linearity of the PANIC detectors based on the 
    algorithm described by Bernhard Dorner at PANIC-DEC-TN-02_0_1.pdf.
    """
    def __init__(self, r_offset, model, input_files, out_dir='/tmp', 
                suffix='_LC', force=False, coadd_correction=True):
        """
        Init the object.
        
        Parameters
        ----------
        r_offset : str
            FITS filename of the reference offset (bias) to be used for; it must be 
            subtracted from the input data before applying the model.

        model : str 
            FITS filename of the Non-Linearity model, ie., containing polynomial 
            coeffs (4th order) for correction that must has been previously 
            computed. It must be a cube with 4 planes (a plane for each coeff c4
            to c1; c0 (intercept) is not used in the correction and not stored in the cube), 
            and one single extension for the full detector. Planes definitions:

                plane_0 = coeff_4 
                plane_1 = coeff_3 
                plane_2 = coeff_2 
                plane_3 = coeff_1 
        
        input_files: list 
            A list of FITS files to be corrected (non MEF FITS).

        out_dir: str
            Directory where new corredted files will be saved

        suffix: str
            Suffix to add to the input filename to generate the output filename.

        force: bool
            If true, no check of input raw header is done (NCOADDS, DETROT90, 
            INSTRUME,...)
            
        coadd_correction: bool
            If true and NCOADDS>1, divide the data by NCOADDS, apply NLC and then 
            multiply by NCOADDS.

        Returns
        -------
        outfitsname: list
            The list of new corrected FITS files created.
        
        """
        self.input_files = input_files
        self.model = model
        self.r_offset = r_offset
        self.suffix = suffix
        self.out_dir = out_dir
        self.force = force
        self.coadd_correction = coadd_correction
        
        if not os.access(self.out_dir, os.F_OK):
            try:
                os.mkdir(self.out_dir)
            except Exception as e:
                raise e
        
        if len(self.input_files)<1:
            msg = "Found empty list of input files"
            log.error(msg)
            raise Exception(msg)
        
        if not os.path.exists(self.model):
            msg = "Cannot read non-linearity model file '%s'" % self.model
            log.error(msg)
            raise Exception(msg)

    def checkHeader(self, modelHeader, dataHeader):
        """
        Performs some data checking (readmode, orientation, date-obs, 
        savemode,...).

        Parameters
        ----------
        modelHeader: 
            Header of the NLC model.
        dataHeader:
            Header of an raw data file.

        Returns
        -------
           If a non-compliant header is found, some exception will be raised.

        """

        # First, checks model is a MASTER_LINEARITY
        try:
            if modelHeader['PAPITYPE'] != 'MASTER_LINEARITY':
                log.warning('PAPITYPE not found in header')
                # raise ValueError('Wrong type of nonlinearity correction file')
        except Exception as ex:
            log.warning('Cannot read PAPITYPE in header')

        # Check input files are non-integrated files (NCOADDS)
        # It is done on applyModel, where can be skipped.
        # if dataHeader['NCOADDS'] > 1:
        #    log.info("Found a wrong type of source file. Use -F to user ncoadd correction")
        #    raise ValueError('Wrong type of file. Only non-integrated files (NCOADDS=1) allowed.')

        # Check NLC model is used with newer data (USE_AFTER->USE_AFT)
        datadate = dateutil.parser.parse(dataHeader['DATE-OBS'])
        nldate = dateutil.parser.parse(modelHeader['USE_AFT'])
        if datadate < nldate:
            log.warning('Nonlinearity calibration too new for input data')
            # raise ValueError('Nonlinearity calibration too new for input data')           
        
        # Check some other keys related with READOUT configuration 
        keys = ['INSTRUME', 'PREAD', 'PSKIP', 'LSKIP', 'READMODE', 'IDLEMODE', 'IDLETYPE']
        for key in keys:
            if str(dataHeader[key]).lower() != str(modelHeader[key]).lower():
                log.warning('Mismatch in header data for keyword \'%s\'' %key)
                #raise ValueError('Mismatch in header data for keyword \'%s\'' %key)            
        
        # some may not be present in old data
        keys = ['DETROT90', 'DETXYFLI']
        for key in keys:
            if not key in dataHeader:
                print('Warning: key \'%s\' not in data header' % key)
            elif dataHeader[key] != modelHeader[key]:
                raise ValueError('Mismatch in header data for keyword \'%s\'' %key)
        keys = ['B_EXT', 'B_DSUB', 'B_VREST', 'B_VBIAG']
        for key in keys:
            if dataHeader[key + '1'] != modelHeader[key + '1']:
                    raise ValueError('Mismatch in header data for keyword \'%s1\'' %(key))


    def parse_detsec(self, detsec_str):
        """Parses DETSEC string in the format '[x1:x2,y1:y2]' into integer indices."""
        try:
            detsec_str = detsec_str.strip().replace(" ", "").replace("[", "").replace("]", "")
            x_range, y_range = detsec_str.split(",")
            x1, x2 = map(int, x_range.split(":"))
            y1, y2 = map(int, y_range.split(":"))

            # **Convert 1-based indices to 0-based**
            x1 -= 1
            x2 -= 1
            y1 -= 1
            y2 -= 1

            # Fix for inclusive slicing
            x2 += 1  # Include last column
            y2 += 1  # Include last row
            # print (f"Parsed DETSEC: x1={x1}, x2={x2}, y1={y1}, y2={y2}")
            return x1, x2, y1, y2
        except Exception as e:
            log.error(f"Failed to parse DETSEC: {detsec_str}. Error: {e}")
            raise ValueError(f"Invalid DETSEC format: {detsec_str}")


    def applyModel(self, data_file):
        """
        Do the Non-linearity correction using the supplied model. In principle,
        it should be applied to all raw images (darks, flats, science, ...).
        
        Parameters
        ----------
        data_file: str
            input data FITS filename to be corrected.

        Returns
        -------
        outfitsname: str
            The list of new corrected files created.
                
        """   
        
        # load raw data file
        hdulist = fits.open(data_file)
        dataheader = hdulist[0].header
        
        # Check if input files are in SEF format
        to_delete = None
        if len(hdulist) > 1:
            # we do not allow MEF
            log.warning("Mismatch in header data format. MEF file not supported")
            hdulist.close()
            raise ValueError('Mismatch in header data format. Only MEF files allowed.')

        # load reference offset file
        if self.r_offset:
            try:
                ref_offset_hdu = fits.open(self.r_offset)
                ref_offset = ref_offset_hdu[0].data.astype('float32')
            except Exception as e:
                log.error("Cannot read reference offset file '%s'" % self.r_offset)
                raise e
        else:
            ref_offset = np.zeros(hdulist[0].data.shape, dtype='float32')
            log.warning("No reference offset file provided. Using zero offset.")

        
        # load model
        nlhdulist = fits.open(self.model)
        nlheader = nlhdulist[0].header

        # Check headers
        try:
            if not self.force:
                self.checkHeader(nlheader, dataheader)
        except Exception as e:
            log.error("Mismatch in header data for input NLC model %s"%str(e))
            raise e

        # Creates output fits HDU
        linhdu = fits.PrimaryHDU()
        linhdu.header = dataheader.copy()
        hdus = []

        # ---
        # another way would be to loop until the correct one is found
        datadetsec = str(hdulist[0].header['DETSEC']).replace(" ", "") if isinstance(hdulist[0].header['DETSEC'], str) else str(hdulist[0].header['DETSEC'])
        nldetsec = str(nlhdulist[0].header['DETSEC']).replace(" ", "") if isinstance(nlhdulist[0].header['DETSEC'], str) else str(nlhdulist[0].header['DETSEC'])
        if datadetsec != nldetsec:
            log.warning("Mismatch of detector sections")
            #raise ValueError('Mismatch of detector sections')
        
        datadetid = str(hdulist[0].header['CHIPID']).strip() if isinstance(hdulist[0].header['CHIPID'], str) else str(hdulist[0].header['CHIPID'])
        # nldetid = nlhdulist['LINMAX'].header['CHIPID']
        nldetid = str(nlhdulist[0].header['CHIPID']).strip() if isinstance(nlhdulist[0].header['CHIPID'], str) else str(nlhdulist[0].header['CHIPID'])
        if datadetid != nldetid:
            log.warning("Mismatch of detector IDs")
            # raise ValueError('Mismatch of detector IDs')

        # Work around to correct data when NCOADDS > 1
        if hdulist[0].header['NCOADDS'] > 1:
            if self.coadd_correction:
                log.info("NCOADDS > 1; Doing ncoadd correction...")
                n_coadd = hdulist[0].header['NCOADDS']
            else:
                log.info("Found a wrong type of source file. Use -c to user ncoadd correction")
                raise ValueError('Cannot apply model, found NCOADDS > 1.')
        else:
            n_coadd = 1
        
        # 2024-02-23: JMIM
        # Parche provisional para poder procesar imagenes con NEXP != NCOADD que se crearon "mal"
        # en convRaw2CDS.py (ya parcheado tambien)
        # 2025-02-23: JMIM: Although this convRaw2CDS is already fixed, it is a good idea to keep it
        nexp = hdulist[0].header['NEXP']
        if len(hdulist[0].data.shape) > 2:
            cube_layers = hdulist[0].data.shape[-1]
        else:
            cube_layers = 1

        if nexp > 1 and n_coadd == 1 and cube_layers == 1:
            log.warning("Overwriting n_coadd with nexp. Ensure this is the intended behavior.")
            n_coadd = nexp
        elif n_coadd == 1:
            n_coadd = 1
        else:
            log.info("Using provided n_coadd value.")
        # Fin-del-parche 

        
        # load file data
        data = hdulist[0].data
        nlmaxs = nlhdulist['LINMAX'].data
        nlpolys = np.rollaxis(nlhdulist['LINPOLY'].data, 0, 3)


        # Check if data is a subset of the full detector
        # (if so, we need to crop the data)
        # Extract subsection using DETSEC
        try:
            x1, x2, y1, y2 = self.parse_detsec(datadetsec)
            nlmaxs_subsection = nlmaxs[y1:y2, x1:x2]
            nlpolys_subsection = nlpolys[y1:y2, x1:x2, :]  # Assuming last dimension is polynomial coefficients
            sub_r_offset = ref_offset[y1:y2, x1:x2]
        except ValueError:
            log.warning("Using full data since DETSEC parsing failed")
            nlmaxs_subsection = nlmaxs
            nlpolys_subsection = nlpolys

        # Print x,y ranges for debugging
        log.debug(f"Using DETSEC: x1={x1}, x2={x2}, y1={y1}, y2={y2}")

        # subtract reference offset taking into account the coadd_correction (repetitions integrated)
        log.info("Subtracting reference offset")
        log.debug("Mean value of reference offset: %s" % str(np.mean(ref_offset)))
        log.debug("Mean value of data: %s" % str(np.mean(data)))
        data = data - sub_r_offset*n_coadd
        log.debug("Mean value of data after offset: %s" % str(np.mean(data)))
        # Correct data from n_coadd  
        data = data / n_coadd

        # calculate linear corrected data
        lindata = self.polyval_map(nlpolys_subsection, data)
        
        # mask saturated inputs - to use nan it has to be a float array
        lindata[data > nlmaxs_subsection] = np.nan
        # mask where max range is nan
        # (first, take into account the option of cubes as input images) 
        if len(lindata.shape) == 3: 
            # we have a 3D image (cube)
            for i in range(lindata.shape[0]):
                lindata[i, np.isnan(nlmaxs_subsection)] = np.nan
        else:
            # we have a single 2D image
            lindata[np.isnan(nlmaxs_subsection)] = np.nan

        
        # Undo the coadd_correction
        lindata = lindata * n_coadd       
        linhdu.data = lindata.astype('float32')
        
        # add some info in the header
        linhdu.header['HISTORY'] = 'Nonlinearity correction applied'
        linhdu.header['HISTORY'] = 'Nonlinearity data: %s' %nlheader['ID']
        linhdu.header['HISTORY'] = '<-- The PANIC team made this on 2025/05/30'
        linhdu.header.set('PAPIVERS', __version__,'PANIC Pipeline version')
        linhdulist = fits.HDUList([linhdu])
        
        # Compose output filename
        mfnp = os.path.basename(data_file).partition('.fits')
        # add suffix before .fits extension, or at the end if no such extension present
        outfitsname = self.out_dir + '/' + mfnp[0] + self.suffix + mfnp[1] + mfnp[2]
        outfitsname = os.path.normpath(outfitsname)

        # overwrite the output file if exists
        linhdulist.writeto(outfitsname, overwrite=True)

        # close input files
        hdulist.close()
        nlhdulist.close()
        ref_offset_hdu.close()
        linhdulist.close()

        log.info("Non-linearity correction applied to file '%s'" % outfitsname)
        
        # remove the input file if it is a temporary file 
        if to_delete:
            os.unlink(to_delete)

        return outfitsname


    def runMultiNLC(self):
        """
        Run a parallel proceesing of NL-correction for the input files taking
        advantege of multi-core CPUs.

        Returns
        -------
        On succes, a list with the filenames of the corrected files.
        """

        # use all CPUs available in the computer
        n_cpus = multiprocessing.cpu_count()
        log.debug("N_CPUS :" + str(n_cpus))
        pool = multiprocessing.Pool(processes=n_cpus)
        
        results = []
        solved = []
        for i_file in self.input_files:
            red_parameters = [i_file]
            try:
                # Instead of pool.map() that blocks until
                # the result is ready, we use pool.map_async()
                results += [pool.map_async(unwrap_self_applyModel, 
                        zip([self]*len(red_parameters), red_parameters) )]
            except Exception as e:
                log.error("Error processing file: " + i_file)
                log.error(str(e))
                
        for result in results:
            try:
                result.wait()
                # the 0 index is *ONLY* required if map_async is used !!!
                solved.append(result.get()[0])
                log.info("New file created => %s"%solved[-1])
            except Exception as e:
                log.error("Cannot process file \n" + str(e))
                
        # Prevents any more tasks from being submitted to the pool.
        # Once all the tasks have been completed the worker 
        # processes will exit.
        pool.close()

        # Wait for the worker processes to exit. One must call 
        #close() or terminate() before using join().
        pool.join()
        
        log.info("Finished parallel NL-correction")
        
        return solved

    def polyval_map(self, poly, map):
        """
        Evaluate individual polynomials on an array. Looping over each pixel
        is stupid, therefore we loop over the order and calculate the
        polynomial directly.
        Note: The output is a float array!
        
        Input
        -----
        poly : array_like
               Polynomial coefficients without constant offset. The order
               must be along the last axis.
        map : array_like
              Data array, that can be a cube of 2D images.
              
        Returns
        -------
        polymap : array_like
                  Result of evaluation, same shape as map, dtype float
        """

        order = poly.shape[-1]
        polymap = map * 0.
        for io in range(order):
            polymap += poly[Ellipsis, -io-1] * map**(io+1)
        return polymap

################################################################################
# main


def main(arguments=None):

    desc = """Performs the non-linearity correction of the PANIC raw data files
using the proper NL-Model (FITS file). Raw data files must be SEF files; if 
SEF-cubes, each plane is corrected individually.
"""
    parser = argparse.ArgumentParser(description=desc)
    # Basic inputs
    parser.add_argument("-m", "--model",
                  action="store", dest="model",
                  help="FITS SEF (can be a cube) file of polinomial coeffs (c4, c3, c2, c1) of the NL model.")

    parser.add_argument("-r", "--reference_offset",
                  action="store", dest="r_offset",
                  help="FITS file of reference offset (bias) to be used for previosly to apply the model")

    parser.add_argument("-i", "--input_file",
                  action="store", dest="input_file",
                  help="FITS file to be corrected.")

    parser.add_argument("-s", "--source",
                  action="store", dest="source_file_list",
                  help="Source file list of FITS files to be corrected.")

    parser.add_argument("-o", "--out_dir", type=str, dest="out_dir",
                  action="store", default="/tmp",
                  help="filename of out data file (default: %(default)s)")

    parser.add_argument("-S", "--suffix", type=str,
                  action="store", dest="suffix", default="_NLC", 
                  help="Suffix to use for new corrected files (default: %(default)s)")

    parser.add_argument("-f", "--force",
                  action="store_true", dest="force", default=False, 
                  help="Force Non-linearity correction with no check of header"
                       "values (NCOADD, DATE-OBS, DETROT90, ...")

    parser.add_argument("-c", "--coadd_correction",
                  action="store_true", dest="coadd_correction", default=True, 
                  help="Force NCOADDS correction and apply NLC")
    
    args = parser.parse_args()
    
    if len(sys.argv[1:]) < 1:
       parser.print_help()
       sys.exit(0)

    # Check required parameters
    if ((not args.source_file_list and not args.input_file) or not args.out_dir
        or not args.model) or not args.r_offset: # args is the leftover positional arguments after all options have been processed
        parser.print_help()
        parser.error("incorrect number of arguments ")
    
    if args.input_file and os.path.isfile(args.input_file):
        filelist = [args.input_file]
    elif args.source_file_list and os.path.isfile(args.source_file_list):
        # Read the source file list     
        filelist = [line.replace("\n", "") for line in fileinput.input(args.source_file_list)]
    else:
        parser.print_help()
        parser.error("incorrect number of arguments " )

    NLC = NonLinearityCorrection(args.r_offset, args.model, filelist, args.out_dir,
                                 args.suffix, args.force,
                                 args.coadd_correction)

    try:
        corr = NLC.runMultiNLC()
    except Exception as e:
        log.error("Error running NLC: %s"%str(e))
        raise e

    print("\nCorrected files: ", corr)
    
    """
    # Non parallel processing
    for i_file in filelist:
        try:
            NLC.applyModel(i_file)
        except Exception,e:
            log.error("Error applying NLC model to file '%s': %s"%(i_file, str(e)))
    """

######################################################################
if __name__ == "__main__":
    sys.exit(main())

