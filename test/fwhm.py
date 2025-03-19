import numpy as np
import sep
from astropy.io import fits  # For FITS files (optional)
import matplotlib.pyplot as plt
import sys
from astropy.visualization import ZScaleInterval,ImageNormalize

my_image = sys.argv[1]

# Step 1: Load the image (replace with your image data)
with fits.open(my_image) as hdul:
    data = hdul[0].data.astype(np.float64)  # 2D array, ensure float64

# Step 2: Estimate and subtract the background
bkg = sep.Background(data)  # Background estimation
data_sub = data - bkg.back()  # Subtract background
noise = bkg.globalrms  # Global RMS noise level

# Step 3: Detect objects (stars) in the image
objects = sep.extract(data_sub, thresh=3.0, err=noise)  # Threshold = 1.5 * RMS

# Check if any objects were detected
if len(objects) == 0:
    raise ValueError("No objects detected in the image. Try lowering the detection threshold.")

# Step 4: Calculate SNR and FWHM for each object
snr_values = []
fwhm_values = []
img_height, img_width = data_sub.shape

for obj in objects:
    x, y = int(obj['x']), int(obj['y'])
    
    # Define region bounds with boundary checking
    y_min = max(0, y - 2)  # Ensure not below 0
    y_max = min(img_height, y + 3)  # Ensure not beyond height
    x_min = max(0, x - 2)  # Ensure not below 0
    x_max = min(img_width, x + 3)  # Ensure not beyond width
    
    # Extract region, skip if it’s too small
    region = data_sub[y_min:y_max, x_min:x_max]
    if region.size == 0:  # Skip if region is empty
        continue
    
    # Calculate SNR
    peak_flux = np.max(region)  # Peak value in the region
    snr = peak_flux / noise
    snr_values.append(snr)

    # Calculate FWHM (assuming Gaussian profile)
    sigma_x = obj['a'] / np.sqrt(2 * np.log(2))  # Semi-major axis to sigma
    sigma_y = obj['b'] / np.sqrt(2 * np.log(2))  # Semi-minor axis to sigma
    fwhm_x = 2.355 * sigma_x
    fwhm_y = 2.355 * sigma_y
    fwhm_avg = (fwhm_x + fwhm_y) / 2
    fwhm_values.append(fwhm_avg)

print(np.median(fwhm_values))


# Check if any valid objects remain
if not snr_values:
    raise ValueError("No valid regions could be extracted. Check image dimensions or object positions.")

# Convert to NumPy arrays
snr_values = np.array(snr_values)
fwhm_values = np.array(fwhm_values)

# Step 5: Filter objects with the best SNR (top 10%)
percentile = 60
snr_threshold = np.nanpercentile(snr_values, percentile)
high_snr_mask = snr_values >= snr_threshold
print("SNR=",snr_values)
print(snr_threshold)
# Step 6: Compute mean FWHM for high-SNR objects
mean_fwhm = np.mean(fwhm_values[high_snr_mask])
num_stars = np.sum(high_snr_mask)
print(f"Mean FWHM of {num_stars} high-SNR stars: {mean_fwhm:.2f} pixels  {mean_fwhm*0.3761:.2f} arcsec")
print(f"SNR threshold (top {100 - percentile}%): {snr_threshold:.2f}")



background = np.median(bkg)
plt.figure(figsize=(10, 8))
z = ZScaleInterval()
z1,z2 = z.get_limits(data_sub)
norm = ImageNormalize(data_sub, interval=z)
#plt.imshow(data_sub, cmap='gray', vmin=0.5*background, vmax=2*background, interpolation='nearest')
plt.imshow(data_sub, cmap='gray', vmin=z1, vmax=z2, interpolation='nearest')
#plt.imshow(data_sub, cmap='gray', norm=norm)

# Optional: Visualize the image and high-SNR stars
#plt.imshow(data_sub, origin='lower', cmap='gray')
plt.plot(objects['x'][high_snr_mask], objects['y'][high_snr_mask], 'ro', ms=5, alpha=0.5, label='High-SNR stars')
plt.legend()
plt.show()
