import numpy as np
import argparse
from astropy.io import fits
from astropy.stats import sigma_clipped_stats
from photutils.detection import DAOStarFinder
from photutils.psf import fit_2dgaussian

def estimate_fwhm(fits_file):
    # Load the FITS image
    with fits.open(fits_file) as hdul:
        image_data = hdul[0].data

    # Mask NaN and infinite values in the image
    image_data = np.ma.masked_invalid(image_data)

    # Optionally replace masked values with the median of the data (optional step)
    if np.ma.is_masked(image_data):
        image_data = np.ma.filled(image_data, np.ma.median(image_data))

    # Compute background statistics
    mean, median, std = sigma_clipped_stats(image_data, sigma=3.0)

    # Detect sources using DAOStarFinder
    daofind = DAOStarFinder(fwhm=3.0, threshold=5.0 * std)  
    sources = daofind(image_data - median)

    if sources is None or len(sources) == 0:
        print("No sources detected.")
        return

    print(f"Detected {len(sources)} sources.")

    fwhm_list = []
    
    for x, y in zip(sources["xcentroid"], sources["ycentroid"]):
        # Extract a small region around each source for Gaussian fitting
        x, y = int(x), int(y)
        cutout = image_data[y-5:y+6, x-5:x+6]  # 11x11 box

        # Ensure cutout is not masked
        if np.ma.is_masked(cutout):
            cutout = np.ma.filled(cutout, np.ma.median(cutout))  # Replace masked areas with median value

        try:
            gauss_fit = fit_2dgaussian(cutout)
            fwhm = 2.355 * np.mean([gauss_fit.x_stddev.value, gauss_fit.y_stddev.value])
            fwhm_list.append(fwhm)
        except Exception as e:
            print(f"Skipping source at ({x}, {y}) due to fitting error: {e}")
            continue  # Skip sources that can't be fitted

    if fwhm_list:
        fwhm_mean = np.mean(fwhm_list)
        print(f"Estimated FWHM: {fwhm_mean:.2f} pixels")
    else:
        print("No valid FWHM measurements.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Estimate FWHM from a FITS image.")
    parser.add_argument("fits_file", type=str, help="Path to the FITS file.")
    args = parser.parse_args()

    estimate_fwhm(args.fits_file)

