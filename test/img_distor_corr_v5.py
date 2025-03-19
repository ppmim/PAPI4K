import numpy as np
import matplotlib.pyplot as plt
import astropy.io.fits as fits
from scipy.optimize import curve_fit
from scipy.interpolate import UnivariateSpline
import sys
from matplotlib.colors import LogNorm  # Import LogNorm here

# Load the corr.fits file
filename = sys.argv[1]
with fits.open(filename) as hdul:
    data = hdul[1].data  # Extract the binary table

# Extract relevant columns
field_x, field_y = data['field_x'], data['field_y']  # Measured x, y positions
index_x, index_y = data['index_x'], data['index_y']  # Catalog-projected x, y positions

field_ra, field_dec = data['field_ra'], data['field_dec']  # Measured RA, Dec
index_ra, index_dec = data['index_ra'], data['index_dec']  # Reference RA, Dec

# Compute positional residuals in pixels
delta_x = field_x - index_x
delta_y = field_y - index_y

# Compute astrometric residuals in arcseconds
cos_dec = np.cos(np.radians(field_dec))  # RA correction factor
delta_ra = (field_ra - index_ra) * cos_dec * 3600  # Convert degrees to arcsec
delta_dec = (field_dec - index_dec) * 3600  # Convert degrees to arcsec
positional_error = np.sqrt(delta_ra**2 + delta_dec**2)  # Total error per star

# --- Compute Key Astrometric Metrics ---
rms_error = np.sqrt(np.mean(positional_error**2))  # RMS error
mean_error = np.mean(positional_error)  # Mean absolute error (MAE)
std_error = np.std(positional_error)  # Standard deviation
median_error = np.median(positional_error)  # Median error
percentile_95 = np.percentile(positional_error, 95)  # 95th percentile

# Maximal shift (maximum positional residual)
max_shift = np.max(positional_error)

# --- Calculate Distortion Percentage ---
# Total squared residuals in pixel space (x and y)
total_squared_residuals = np.sum(delta_x**2 + delta_y**2)

# Total number of stars (area)
num_stars = len(delta_x)

# Calculate distortion percentage as the total squared residuals over the total number of stars
distortion_percentage = (total_squared_residuals / num_stars) * 100


# Optionally normalize by the number of stars (average distortion per star)
average_distortion = total_squared_residuals / num_stars

# Define the total area of the image (in pixels). For example, let's assume the image is of size 1000x1000 pixels.
image_area = 4096 * 4096  # Adjust to your actual image size

# Calculate distortion percentage: (total squared residuals / image area) * 100
distortion_percentage = (total_squared_residuals / image_area) * 100

# Compute the total image size in arcseconds (approximate field size)
# Assuming image size is `width x height` in pixels, and plate scale is `scale_arcsec_per_pixel`
image_width_pixels = max(field_x) - min(field_x)
image_height_pixels = max(field_y) - min(field_y)

# Use an approximate plate scale (arcsec per pixel)
plate_scale = np.mean(positional_error) / np.mean(np.sqrt(delta_x**2 + delta_y**2))
# Compute the field size in arcseconds
field_size = max(image_width_pixels, image_height_pixels) * plate_scale

# Compute SCAMP-like distortion percentage
distortion_percentage = (max_shift / field_size) * 100

# Print Astrometric Performance Metrics
print("\n--- Astrometric Calibration Performance ---")
print(f"RMS Positional Error:     {rms_error:.3f} arcsec , {rms_error/plate_scale:.3f} pixels")
print(f"Mean Positional Error:    {mean_error:.3f} arcsec, {mean_error/plate_scale:.3f} pixels")
print(f"Standard Deviation (σ):   {std_error:.3f} arcsec, {std_error/plate_scale:.3f} pixels")
print(f"Median Positional Error:  {median_error:.3f} arcsec, {median_error/plate_scale:.3f} pixels")
print(f"95th Percentile Error:    {percentile_95:.3f} arcsec, {percentile_95/plate_scale:.3f} pixels")
print(f"Maximal Positional Shift: {max_shift:.3f} arcsec, {max_shift/plate_scale:.3f} pixels")
print(f"Distortion Percentage:    {distortion_percentage:.2f}%")
print("-------------------------------------------")

# Scale factor for vector length
scale_factor = 50  # Adjust this value to change vector lengths

# --- 1. Distortion Vector Field ---
plt.figure(figsize=(8, 6))
plt.quiver(index_x, index_y, delta_x * scale_factor, delta_y * scale_factor, 
           angles="xy", scale_units="xy", scale=1, color="r", alpha=0.6)
plt.xlabel("X (pixels)")
plt.ylabel("Y (pixels)")
plt.title("Image Distortion Vector Field (Scaled) - RMS= %.3f (px)"%(rms_error/plate_scale))
plt.gca().invert_yaxis()
plt.show()

# --- 2. Heatmap of Positional Errors ---
plt.figure(figsize=(8, 6))

# Define grid resolution
num_bins_x, num_bins_y = 100, 100  # Adjust for smoother/finer resolution
x_bins = np.linspace(min(field_x), max(field_x), num_bins_x)
y_bins = np.linspace(min(field_y), max(field_y), num_bins_y)

# Create 2D histogram
heatmap, xedges, yedges = np.histogram2d(field_x, field_y, bins=[x_bins, y_bins], weights=positional_error)

# Plot heatmap with log scale for better contrast
plt.pcolormesh(xedges, yedges, heatmap.T, cmap="plasma", shading="auto")# norm=LogNorm())  # Use LogNorm here
plt.colorbar(label="Astrometric Error (arcsec)")
plt.xlabel("X (pixels)")
plt.ylabel("Y (pixels)")
plt.title("Astrometric Uncertainty Heatmap")
plt.gca().invert_yaxis()
plt.show()




# --- 3. Separate 1D Residual Histograms for RA and Dec ---
plt.figure(figsize=(8, 6))

# Plot RA residuals
plt.hist(delta_ra, bins=50, color="royalblue", edgecolor="black", alpha=0.7, label="RA Residuals")
plt.axvline(rms_error, color="red", linestyle="dashed", linewidth=2, label=f"RMS Error = {rms_error:.3f} arcsec")
plt.axvline(median_error, color="green", linestyle="dashed", linewidth=2, label=f"Median Error = {median_error:.3f} arcsec")
plt.xlabel("RA Residuals (arcsec)")
plt.ylabel("Number of Stars")
plt.title("Histogram of RA Residuals")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.6)
plt.show()

# Plot Dec residuals
plt.figure(figsize=(8, 6))
plt.hist(delta_dec, bins=50, color="darkorange", edgecolor="black", alpha=0.7, label="Dec Residuals")
plt.axvline(rms_error, color="red", linestyle="dashed", linewidth=2, label=f"RMS Error = {rms_error:.3f} arcsec")
plt.axvline(median_error, color="green", linestyle="dashed", linewidth=2, label=f"Median Error = {median_error:.3f} arcsec")
plt.xlabel("Dec Residuals (arcsec)")
plt.ylabel("Number of Stars")
plt.title("Histogram of Dec Residuals")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.6)
plt.show()

# --- 4. 1D Histogram of Positional Errors ---
plt.figure(figsize=(8, 6))
plt.hist(positional_error, bins=50, color="royalblue", edgecolor="black", alpha=0.7)
plt.axvline(rms_error, color="red", linestyle="dashed", linewidth=2, label=f"RMS Error = {rms_error:.3f} arcsec")
plt.axvline(median_error, color="green", linestyle="dashed", linewidth=2, label=f"Median Error = {median_error:.3f} arcsec")
plt.axvline(percentile_95, color="purple", linestyle="dashed", linewidth=2, label=f"95% Error = {percentile_95:.3f} arcsec")
plt.xlabel("Positional Error (arcsec)")
plt.ylabel("Number of Stars")
plt.title("Histogram of Astrometric Errors")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.6)
plt.show()


# --- 2. Heatmap of Positional Errors ---
error_magnitude = np.sqrt(delta_x**2 + delta_y**2)
plt.figure(figsize=(8, 6))
plt.hexbin(field_x, field_y, C=error_magnitude, gridsize=50, cmap="plasma")
plt.colorbar(label="Distortion Magnitude (pixels)")
plt.xlabel("X (pixels)")
plt.ylabel("Y (pixels)")
plt.title("Distortion Heatmap")
plt.gca().invert_yaxis()
plt.show()

# --- 5. Radial Distortion Profile ---
image_center = (np.median(field_x), np.median(field_y))
print(image_center)
radii = np.sqrt((field_x - image_center[0])**2 + (field_y - image_center[1])**2)
plt.figure(figsize=(8, 6))
plt.scatter(radii, error_magnitude, alpha=0.5, s=5)
plt.xlabel("Distance from Image Center (pixels)")
plt.ylabel("Distortion Magnitude (pixels)")
plt.title("Radial Distortion Profile")
plt.show()


# Assign stars to each diagonal and vertical/horizontal categories
def get_diagonal(x, y, center_x, center_y):
    angle = np.arctan2(y - center_y, x - center_x)
    
    if abs(angle) < np.pi / 4:   # Close to 0 radians → Horizontal
        return "horizontal"
    elif abs(angle) > 3 * np.pi / 4:  # Close to ±π radians → Vertical
        return "vertical"
    elif angle > 0:   # Positive angle → Bottom-left to Top-right diagonal (↘)
        return "diagonal ↘"
    else:  # Negative angle → Top-left to Bottom-right diagonal (↙)
        return "diagonal ↙"


# Smooth fit function (Spline)
def smooth_fit(radii, distortion):
    sorted_indices = np.argsort(radii)
    radii_sorted = radii[sorted_indices]
    distortion_sorted = distortion[sorted_indices]
    spline = UnivariateSpline(radii_sorted, distortion_sorted, s=None)
    return radii_sorted, spline(radii_sorted)

# -- Radial profiles 
def radial_profiles(field_x, field_y, index_x, index_y):
    center_x, center_y = np.median(field_x), np.median(field_y)
    #x_model, y_model = fit_polynomial(field_x, field_y, index_x, index_y)
    #delta_x, delta_y = field_x - x_model, field_y - y_model
    distortion = np.sqrt(delta_x**2 + delta_y**2)
    radii = np.sqrt((field_x - center_x)**2 + (field_y - center_y)**2)
    labels = np.array([get_diagonal(x, y, center_x, center_y) for x, y in zip(field_x, field_y)])
    
    plt.figure(figsize=(10, 8))

    for diag in ["diagonal ↘", "diagonal ↙", "horizontal", "vertical"]:
        mask = labels == diag
        radii_diag, distortion_diag = radii[mask], distortion[mask]
        plt.scatter(radii_diag, distortion_diag, label=diag, s=10, alpha=0.3)
        

        # Fit a smooth curve to the radial profile
        if len(radii_diag) > 3:  # Spline needs at least 4 points for reasonable fit
            radii_smooth, distortion_smooth = smooth_fit(radii_diag, distortion_diag)
            plt.plot(radii_smooth, distortion_smooth, linewidth=2)

    plt.xlabel("Distance from Center (pixels)")
    plt.ylabel("Distortion Magnitude (pixels)")
    plt.title("Smoothed Radial Distortion Profiles")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.show()

radial_profiles(field_x, field_y, index_x, index_y)


## --- Binned average profile

def binned_average_profile(radii, distortion, bins=20):
    bin_edges = np.linspace(min(radii), max(radii), bins + 1)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    binned_means = np.array([
        np.mean(distortion[(radii >= bin_edges[i]) & (radii < bin_edges[i+1])])
        for i in range(bins)
    ])
    return bin_centers, binned_means

plt.figure(figsize=(10, 8))
center_x, center_y = np.median(field_x), np.median(field_y)
distortion = np.sqrt(delta_x**2 + delta_y**2)
radii = np.sqrt((field_x - center_x)**2 + (field_y - center_y)**2)
labels = np.array([get_diagonal(x, y, center_x, center_y) for x, y in zip(field_x, field_y)])
for diag in ["diagonal ↘", "diagonal ↙", "horizontal", "vertical"]:
    mask = labels == diag
    radii_diag, distortion_diag = radii[mask], distortion[mask]
    bin_centers, binned_means = binned_average_profile(radii_diag, distortion_diag)
    plt.plot(bin_centers, binned_means, linewidth=2, label=diag)

plt.xlabel("Distance from Center (pixels)")
plt.ylabel("Average Distortion (pixels)")
plt.title("Binned Radial Distortion Profiles")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.show()
