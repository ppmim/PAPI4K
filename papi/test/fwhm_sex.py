import subprocess
import numpy as np
import pandas as pd
from astropy.io import fits

def estimate_fwhm(image_path, sextractor_path="/usr/local/bin/sex"):
    """Estimate the FWHM of an image using SExtractor."""
    
    # Define SExtractor output catalog
    catalog_name = "sextractor_output.cat"

    # Run SExtractor with required parameters
    command = [
        sextractor_path, image_path,
        "-CATALOG_NAME", catalog_name,
        "-CATALOG_TYPE", "ASCII_HEAD",
        "-DETECT_MINAREA", "5",
        "-DETECT_THRESH", "1.5",
        "-ANALYSIS_THRESH", "1.5",
        "-PHOT_AUTOPARAMS", "2.5, 3.5",
        "-FILTER", "Y"
    ]
    
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print("Error running SExtractor:", e)
        return None

    # Load the SExtractor catalog
    try:
        data = pd.read_csv(catalog_name, comment='#', delim_whitespace=True)
        if 'FWHM_IMAGE' not in data.columns:
            print("FWHM_IMAGE column not found in catalog.")
            return None

        fwhm_values = data["FWHM_IMAGE"].dropna()
        median_fwhm = np.median(fwhm_values)
        
        print(f"Estimated FWHM: {median_fwhm:.2f} pixels")
        return median_fwhm
    except Exception as e:
        print("Error reading SExtractor catalog:", e)
        return None

# Example usage
import sys
image_file = sys.argv[1]  # Replace with your FITS file
fwhm_estimate = estimate_fwhm(image_file)

