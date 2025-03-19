import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy.table import Table
from astropy import units as u
from astropy.stats import sigma_clipped_stats
from astroquery.vizier import Vizier
from photutils.detection import DAOStarFinder
from matplotlib import pyplot as plt
from matplotlib.patches import Arrow
from astropy.coordinates import match_coordinates_sky
from astropy.visualization import ZScaleInterval, ImageNormalize
from astroquery.gaia import Gaia
import warnings
import sys


warnings.filterwarnings('ignore')

def analyze_image_distortion(fits_file, mag_limit=20):
    """
    Analyze image distortion by comparing detected sources with 2MASS catalog.
    
    Parameters:
    -----------
    fits_file : str
        Path to the FITS file with WCS information
    mag_limit : float
        Magnitude limit for 2MASS K-band query
    
    Returns:
    --------
    fig : matplotlib figure
        Figure containing the distortion map
    """
    
    # Read the FITS file
    hdul = fits.open(fits_file)
    data = hdul[0].data
    header = hdul[0].header
    wcs = WCS(header)
    
    # Get image dimensions
    ny, nx = data.shape
    
    # Detect sources in the image
    mean, median, std = sigma_clipped_stats(data, sigma=3.0)
    daofind = DAOStarFinder(fwhm=5.0, threshold=10.*std)
    sources = daofind(data - median)
    
    if sources is None:
        raise ValueError("No sources detected in the image")
    
    # Convert pixel coordinates to world coordinates
    detected_coords = wcs.pixel_to_world(sources['xcentroid'], sources['ycentroid'])
    
    # Query Gaia DR2 catalog
    center_coord = wcs.pixel_to_world(nx/2, ny/2)
    radius = np.sqrt((nx/2)**2 + (ny/2)**2) * wcs.pixel_scale_matrix[0,0] * u.deg
    radius = np.abs(radius)*1.5

    # Construct Gaia query
    #query = f"""
    #SELECT source_id, ra, dec, phot_g_mean_mag, pmra, pmdec
    #FROM gaiadr2.gaia_source
    #WHERE CONTAINS(POINT('ICRS', ra, dec),
    #              CIRCLE('ICRS', {center_coord.ra.deg}, {center_coord.dec.deg}, {radius.value}))=1
    #AND phot_g_mean_mag < {mag_limit}
    #"""
    
    query = f"""
    SELECT ra, dec, pmra, pmdec, phot_g_mean_mag, astrometric_excess_noise
    FROM gaiaedr3.gaia_source
    WHERE 1=CONTAINS(POINT('ICRS', ra, dec),
    CIRCLE('ICRS', {center_coord.ra.deg}, {center_coord.dec.deg}, {radius.value}))
    AND astrometric_params_solved = 31
    AND astrometric_excess_noise < 2
    AND phot_g_mean_mag < 20
    """

    try:
        Gaia.ROW_LIMIT = -1
        # Launch Gaia query
        job = Gaia.launch_job_async(query)
        catalog = job.get_results()
        
        if len(catalog) == 0:
            raise ValueError("No Gaia sources found in the field")            
    except Exception as e:
        print(f"Error querying Gaia catalog: {str(e)}")
        print("Check your internet connection and Gaia service availability")
        return None


        
    # Convert Gaia coordinates to SkyCoord
    gaia_coords = SkyCoord(ra=catalog['ra'],
                          dec=catalog['dec'])

    # Match coordinates using astropy's matching function
    idx_detected, d2d, _ = match_coordinates_sky(gaia_coords, detected_coords)
    
    # Apply distance cut
    max_sep = 5.0 * u.arcsec
    good_matches = d2d < max_sep
    
    # Keep only good matches
    matched_mass = gaia_coords[good_matches]
    matched_detected = detected_coords[idx_detected[good_matches]]
    
    # Convert to pixels
    mass_pixels = wcs.world_to_pixel(matched_mass)
    detected_pixels = wcs.world_to_pixel(matched_detected)


    # Tranlate the matched sources to the pixel coordinates with the origin in the center of the image
    detected_pixels = (detected_pixels[0] - nx/2, detected_pixels[1] - ny/2)
    mass_pixels = (mass_pixels[0] - nx/2, mass_pixels[1] - ny/2)
    
    
    # Calculate positional differences
    dx = detected_pixels[0] - mass_pixels[0]
    dy = detected_pixels[1] - mass_pixels[1]

    # filter_outliers = False
    # if (filter_outliers):
    #     #### Filter out outliers using PCA
    #     from sklearn.decomposition import PCA

    #     # Stack dx, dy as (N, 2) matrix for PCA
    #     displacements = np.vstack((dx, dy)).T

    #     # Apply PCA to find the main direction of displacement
    #     pca = PCA(n_components=1)
    #     pca.fit(displacements)
    #     principal_direction = pca.components_[0]  # Principal axis

    #     # Project each displacement onto the principal axis
    #     projections = displacements @ principal_direction

    #     # Compute standard deviation to filter outliers
    #     std_threshold = 3  # Adjust as needed
    #     mean_proj = np.mean(projections)
    #     std_proj = np.std(projections)

    #     # Keep only vectors close to the main direction
    #     good_indices = np.abs(projections - mean_proj) < std_threshold * std_proj

    #     # Filter dx, dy based on good indices
    #     dx = dx[good_indices]
    #     dy = dy[good_indices]
    #     mass_pixels = (mass_pixels[0][good_indices], mass_pixels[1][good_indices])


    
    # Calculate RMS and display statistics
    positional_error = np.sqrt(dx**2 + dy**2)  # Total error per star
    rms_error = np.sqrt(np.mean(positional_error**2))  # RMS error
    # Calculate mean, median, standard deviation, and 95th percentile
    mean_error = np.mean(positional_error)
    median_error = np.median(positional_error)
    std_error = np.std(positional_error)
    percentile_95 = np.percentile(positional_error, 95)
    percentile_98 = np.percentile(positional_error, 98) 
    max_shift = np.max(positional_error)
    
    # Computer the imageh distortion in %
    field_size = max(nx, ny) * 0.3758
    distortion_percentage = (max_shift / field_size) * 100
    distortion_percentage_rms = (rms_error / field_size) * 100
    distortion_percentage_95 = (percentile_95 / field_size) * 100
    # Compute distortion percentage of the maximiun shift in pixels, as a fraction of the matching mass_pixels
    # Find index  the maximum shift in pixels in dx, dy
    max_shift_index = np.argmax(positional_error)   
    max_shift = positional_error[max_shift_index]
    predicted_max_shift = np.sqrt(mass_pixels[0][max_shift_index]**2 + mass_pixels[1][max_shift_index]**2)
    new_distortion_percentage = (max_shift / predicted_max_shift) * 100 
    

    print("\n--- Astrometric Calibration Performance ---\n")
    print("***Values BEFORE filtering:")
    print(f"RMS Positional Error:     {rms_error:.3f} pixels")
    print(f"Mean Positional Error:    {mean_error:.3f} pixels")
    print(f"Standard Deviation (σ):   {std_error:.3f} pixels")
    print(f"Median Positional Error:  {median_error:.3f} pixels")
    print(f"95th Percentile Error:    {percentile_95:.3f} pixels")
    print(f"Maximal Positional Shift: {max_shift:.3f} pixels")
    print(f"Number of sources BEFORE filtering: {len(positional_error)}") 
    # print distortion percentage
    print(f"Distortion Percentage (max):    {distortion_percentage:.2f}%")
    print(f"Distortion Percentage (rms_error):    {distortion_percentage_rms:.2f}%")
    print(f"Distortion Percentage (95th percentile):    {distortion_percentage_95:.2f}%")
    print(f"New Distortion Percentage (Zemax style):    {new_distortion_percentage:.2f}%")
    # print detected pixel coordinates of the maximum shift
    print(f"Detected pixel coordinates of the maximum shift: {detected_pixels[0][max_shift_index]}, {detected_pixels[1][max_shift_index]}")
    print(f"Predicted pixel coordinates of the maximum shift: {mass_pixels[0][max_shift_index]}, {mass_pixels[1][max_shift_index]}")
    print("-------------------------------------------") 

    ####---------------------------------------------------
    #### --- Filter out dx, dy values that are above percentile_98, only for plotting purposes
    good_indices = positional_error < percentile_98
    dx = dx[good_indices]   
    dy = dy[good_indices]
    detected_pixels = (detected_pixels[0][good_indices], detected_pixels[1][good_indices])
    mass_pixels = (mass_pixels[0][good_indices], mass_pixels[1][good_indices])
    positional_error = positional_error[good_indices]
    ####---------------------------------------------------

    
    # Compute distortion percentage of the maximiun shift in pixels, as a fraction of the matching mass_pixels
    # Find index  the maximum shift in pixels in dx, dy
    max_shift_index = np.argmax(positional_error)   
    max_shift = positional_error[max_shift_index]
    predicted_max_shift = np.sqrt(mass_pixels[0][max_shift_index]**2 + mass_pixels[1][max_shift_index]**2)
    new_distortion_percentage = (max_shift / predicted_max_shift) * 100 



    # Calculate and display statistics
    rms_error = np.sqrt(np.mean(positional_error**2))  # RMS error
    mean_error = np.mean(positional_error)
    median_error = np.median(positional_error)
    std_error = np.std(positional_error)
    percentile_95 = np.percentile(positional_error, 95)
    percentile_98 = np.percentile(positional_error, 98) 
    max_shift = np.max(positional_error)
    

    # Computer the imageh distortion in %
    field_size = max(nx, ny) * 0.3758
    distortion_percentage = (max_shift / field_size) * 100
    distortion_percentage_rms = (rms_error / field_size) * 100
    distortion_percentage_95 = (percentile_95 / field_size) * 100


    # printout values in console, both in pixels and arcseconds
    print("\n--- Values AFTER filtering:")
    print(f"Number of sources after filtering: {len(positional_error)}")
    print(f"RMS Positional Error:     {rms_error:.3f} pixels")
    print(f"Mean Positional Error:    {mean_error:.3f} pixels")
    print(f"Standard Deviation (σ):   {std_error:.3f} pixels")
    print(f"Median Positional Error:  {median_error:.3f} pixels")
    print(f"95th Percentile Error:    {percentile_95:.3f} pixels")
    print(f"Maximal Positional Shift: {max_shift:.3f} pixels")
    # print distortion percentage
    print(f"Distortion Percentage (max):    {distortion_percentage:.2f}%")
    print(f"Distortion Percentage (rms_error):    {distortion_percentage_rms:.2f}%")
    print(f"Distortion Percentage (95th percentile):    {distortion_percentage_95:.2f}%")
    print(f"New Distortion Percentage (Zemax style):    {new_distortion_percentage:.2f}%")
    # print detected pixel coordinates of the maximum shift
    print(f"Detected pixel coordinates of the maximum shift: {detected_pixels[0][max_shift_index]}, {detected_pixels[1][max_shift_index]}")
    print(f"Predicted pixel coordinates of the maximum shift: {mass_pixels[0][max_shift_index]}, {mass_pixels[1][max_shift_index]}")
    print("-------------------------------------------")        

    # Plot image with distortion vectors
    # Create figure with WCS projection
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection=wcs)
    
    # Set up ZScale
    zscale = ZScaleInterval()
    z1,z2 = zscale.get_limits(data)
    # bgnd = 2965.0
    norm = ImageNormalize(data, interval=zscale)
    
    
    # 1. Plot image with ZScale normalization
    #imshow(data, cmap='gray', vmin=0.5*bgnd, vmax=2*bgnd, interpolation='nearest')
    #im = ax.imshow(data, cmap='gray', norm=norm)
    
    im = ax.imshow(data, cmap='gray', vmin=z1, vmax=z2)#, interpolation='nearest')
    plt.colorbar(im, label='Counts')
    
    # Revert coordinates transformation to plot sources
    # Tranlate the matched sources to the pixel coordinates with the origin in the center of the image
    detected_pixels = (detected_pixels[0] + nx/2, detected_pixels[1] + ny/2)
    #mass_pixels = (mass_pixels[0] + nx/2, mass_pixels[1] + ny/2)

    # 2. Plot distortion vectors
    scale_factor = 20  # Adjust this to make vectors more visible
    for i in range(len(dx)):
        #ax.add_patch(Arrow(mass_pixels[0][i], mass_pixels[1][i],
        #                  dx[i]*scale_factor, dy[i]*scale_factor,
        #                  width=20, color='red', alpha=0.5))
        ax.add_patch(Arrow(detected_pixels[0][i], detected_pixels[1][i],
                          dx[i]*scale_factor, dy[i]*scale_factor,
                          width=20, color='red', alpha=0.5))
    
    # Add WCS grid
    ax.grid(color='white', ls='solid', alpha=0.5)
    ax.set_xlabel('Right Ascension (J2000)')
    ax.set_ylabel('Declination (J2000)')

    ax.set_title(f'Image Distortion Map (Max.Shift: {max_shift:.2f} pixels {new_distortion_percentage: .2f} %)\n'
                 f'Matched sources: {len(dx)}')
    
    # --- 2nd Distortion Vector Field ---
    plt.figure(figsize=(8, 6))
    plt.quiver(detected_pixels[0], detected_pixels[1], dx * scale_factor, dy * scale_factor, 
            angles="xy", scale_units="xy", scale=1, color="r", alpha=0.6)
    plt.xlabel("X (pixels)")
    plt.ylabel("Y (pixels)")
    plt.title(f'Image Distortion Vector Field (Scaled by: {scale_factor: 2d})"\n'
                f"RMS Positional Error: {rms_error:.3f} pixels") 
    plt.title(f'Image Distortion Vector Field scaled by {scale_factor: 2d} (Max.Shift: {max_shift:.2f} pixels {new_distortion_percentage: .2f} %)\n'
                 f'Matched sources: {len(dx)}')
    #plt.gca().invert_yaxis()
    plt.show()



    # --- 4. 1D Histogram of Positional Errors ---
    plt.figure(figsize=(8, 6))
    plt.hist(positional_error, bins=50, color="royalblue", edgecolor="black", alpha=0.7)
    plt.axvline(rms_error, color="red", linestyle="dashed", linewidth=2, label=f"RMS Error = {rms_error:.3f} pixels")
    plt.axvline(median_error, color="green", linestyle="dashed", linewidth=2, label=f"Median Error = {median_error:.3f} pixels")
    plt.axvline(percentile_95, color="purple", linestyle="dashed", linewidth=2, label=f"95% Error = {percentile_95:.3f} pixels")
    plt.xlabel("Positional Error (pixels)")
    plt.ylabel("Number of Stars")
    plt.title("Histogram of Astrometric Errors")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.show()

    # Print additional statistics
    print(f"Total detected sources: {len(sources)}")
    print(f"Total GAIA sources in field: {len(catalog)}")
    print(f"Matched pairs: {len(dx)}")
    print(f"RMS distortion: {rms_error:.3f} pixels")
    
    hdul.close()
    return fig


# Example usage:
image_example = sys.argv[1]
fig = analyze_image_distortion(image_example)
plt.show()


