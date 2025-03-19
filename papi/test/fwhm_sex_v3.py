import sys
import subprocess
import numpy as np

def estimate_fwhm(image_path, sextractor_path="sex", snr_threshold=0.0, ellipticity_threshold=0.2):
    """Estimate the FWHM of an image using SExtractor with filtering for ellipticity and SNR."""

    # Define SExtractor output catalog
    catalog_name = "sextractor_output.cat"

    # Run SExtractor
    command = [
        sextractor_path, image_path,
        "-CATALOG_NAME", catalog_name,
        "-CATALOG_TYPE", "ASCII",
        "-PARAMETERS_NAME", "default.param",  # Ensure this file exists
        "-FILTER_NAME", "default.conv",
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

    # Read and filter the catalog
    fwhm_values = []
    try:
        with open(catalog_name, "r") as file:
            for line in file:
                if line.startswith("#"):
                    continue  # Skip comment lines
                columns = line.split()
                if len(columns) >= 9:  # Ensure required columns exist
                    fwhm = float(columns[3])  # 4th column = FWHM_IMAGE
                    ellipticity = float(columns[4])  # 5th column = ELLIPTICITY
                    flux = float(columns[7])  # 8th column = FLUX_AUTO
                    flux_err = float(columns[8])  # 9th column = FLUXERR_AUTO
                    
                    # Compute SNR and apply filters
                    if flux_err > 0:
                        snr = flux / flux_err
                        if ellipticity < ellipticity_threshold and snr > snr_threshold:
                            fwhm_values.append(fwhm)

        if not fwhm_values:
            print("No valid stars found after filtering.")
            return None

        median_fwhm = np.median(fwhm_values)
        print(f"Estimated FWHM (filtered): {median_fwhm:.2f} pixels")
        return median_fwhm
    except Exception as e:
        print("Error reading SExtractor catalog:", e)
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python estimate_fwhm.py <image.fits>")
        sys.exit(1)
    
    image_file = sys.argv[1]
    estimate_fwhm(image_file)

