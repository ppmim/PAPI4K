import numpy
import sys
import astropy.io.fits as fits


def swap_bpm(master_bpm, output_filename, overwrite=False):
    """
    Swap values in BPM, 0s by 1s, and 1s by 0s.
    """


    # Check input filename is non-MEF
    with fits.open(master_bpm) as myfits:
        if len(myfits) > 1:
            raise Exception("MEF files are not supported yet.")
    
    try:
        # Load Bad Pixels mask (BP=1's)
        bpm_data, bh = fits.getdata(master_bpm, header=True)
        badpix_ones = numpy.where(bpm_data==1)
        badpix_zeros = numpy.where(bpm_data==0)
        bpm_data[badpix_ones] = 0
        bpm_data[badpix_zeros] = 1
        
        bh.set('INSTRUME', 'PANIC')
        bh.set('CAMERA', 'HgCdTe IR-Camera (1 H4RGs)')
        bh.set('FILTER', 'NO      ')
        bh.set('HISTORY', 'BPM Swaped (0s by 1s and 1s by 0s)')

        # Write masked data
        if overwrite:
            fits.writeto(master_bpm, bpm_data, header=bh, overwrite=True)
        else:
            fits.writeto(output_filename, bpm_data.astype(numpy.dtype(numpy.uint8)), header=bh, clobber=True)
    except Exception as e:
        raise e
    else:
        if not overwrite:
            return output_filename
        else:
            return filename

def compose_bpm(bpm_files):
    """
    Compose the input BPM files doing the OR of all them. 
    """
    
    n_files = len(bpm_files)
    sx, sy = 4096
    i = 0
    # bpm_comp = numpy.zeros([n_files, sx, sy], dtype=numpy.float)
    badpix_ones = numpy.fill((sx,sy), False, dtype=bool)
    
    for f in bpm_files:
        try:
            bpm_data, bh = fits.getdata(f, header=True)
            #bpm_comp[i] = bpm_data
            badpix_ones = np.logical_or(numpy.where(bpm_data == 1), badpix_ones)
        except Exception as e:
            print("Error reading %s" %f)
            raise e

    bpm_data[badpix_ones] = 1
    fits.writeto("/tmp/comp_bpm.fits", bpm_data, header=bh, clobber=True)



def main():
    output_filename = sys.argv[1].split('.')[0] + "_swap.fits"
    swap_bpm(sys.argv[1], output_filename)

###############################################################################
if __name__ == "__main__":
    print('Starting BadPixelMap....')
    bpm_files = ["med_badpix_Panic4K_cntsr_low.fits" ]
    #bpm_comp(med_badpix_Panic4K_cntsr_low.fits)
    sys.exit(main())
