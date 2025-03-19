# from astropy.io import fits
# # %pylab
# img = fits.open("/home/jmiguel/DATA/PANIC/2024-12-15_cds/out2/new-image.fits")[0].data
# tbl = fits.open("/home/jmiguel/DATA/PANIC/2024-12-15_cds/out2/corr.fits")[1].data

# rmserr = sqrt(mean((tbl.index_x-tbl.field_x)**2 + (tbl.index_y - tbl.field_y)**2))

# bgnd = mean(tbl.BACKGROUND)
# imshow(img,cmap='gray',vmin=0.5*bgnd,vmax=2*bgnd,interpolation='nearest')
# axis(‘equal’)
# for i in range(len(tbl.FLUX)):
# 	plot(tbl.index_x[i]-1,tbl.index_y[i]-1,'go',markersize=log(tbl.FLUX[i]/10.))
# 	plot(tbl.field_x[i]-1,tbl.field_y[i]-1,'bo',markersize=log(tbl.FLUX[i]/10.))



import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from astropy.visualization import ZScaleInterval,ImageNormalize
import sys

# Load data
image_example = sys.argv[1]
corr_file = sys.argv[2]
img = fits.open(image_example)[0].data
tbl = fits.open(corr_file)[1].data



# Calculate RMS error (astrometric uncertainty)
dx = tbl['index_x'] - tbl['field_x']  # Verify column names
dy = tbl['index_y'] - tbl['field_y']
rmserr = np.sqrt(np.mean(dx**2 + dy**2))
print(f"Astrometric RMS Error: {rmserr:.2f} pixels")

# Create plot
bgnd = np.mean(tbl['BACKGROUND'])
print("Image BACKGROUND",bgnd)
plt.figure(figsize=(10, 8))
z = ZScaleInterval()
z1,z2 = z.get_limits(img)
norm = ImageNormalize(img, interval=z)
plt.imshow(img, cmap='gray', vmin=0.5*bgnd, vmax=2*bgnd, interpolation='nearest')
plt.imshow(img, cmap='gray', vmin=z1, vmax=z2)
plt.imshow(img, cmap='gray', norm=norm)


# Plot detected vs matched positions
for i in range(len(tbl)):
    flux_size = np.log(tbl['FLUX'][i]/10.0)  # Log scaling
    # Ensure minimum marker size to avoid negative values
    markersize = max(flux_size, 1)  # Adjust minimum size as needed
    markersize = 1
    
    plt.plot(tbl['index_x'][i]-1, tbl['index_y'][i]-1, 'go', markersize=markersize)
    plt.plot(tbl['field_x'][i]-1, tbl['field_y'][i]-1, 'bo', markersize=markersize)

plt.axis('equal')  # Fixed quotes
plt.title(f"Astrometric Matches (RMS Error: {rmserr:.2f} pix)")
plt.xlabel("X pixel")
plt.ylabel("Y pixel")
plt.show()



# Create a quiver plot to visualize the distortion
# Extract the relevant columns
field_x = tbl['field_x']
field_y = tbl['field_y']
index_x = tbl['index_x']
index_y = tbl['index_y']

plt.figure(figsize=(10, 8))
plt.quiver(field_x, field_y, dx, dy, angles='xy', scale_units='xy', scale=1, color='blue', alpha=0.5)
plt.scatter(field_x, field_y, c='red', s=10, label='Measured Positions')
plt.xlabel('X (pixels)')
plt.ylabel('Y (pixels)')
plt.title('Image Distortion (Measured to Reference Positions)')
plt.legend()
plt.grid(True)
plt.axis('equal')  # Equal aspect ratio to avoid stretching
plt.show()