#!/usr/bin/env python3

import sys
import numpy as np
import argparse
import warnings

# Astronomical libraries
import astropy.units as u
from astropy.io import fits
from astropy.table import Table
from astropy.coordinates import SkyCoord, match_coordinates_sky
from astropy.stats import sigma_clipped_stats
from astropy.wcs import WCS

# Photometry and source detection
import photutils
from photutils.detection import DAOStarFinder
from photutils.aperture import aperture_photometry, CircularAperture, CircularAnnulus

# Catalog querying
from astroquery.vizier import Vizier

def get_reference_stars(image_header, radius=10*u.arcmin, catalog='II/246'):
    """
    Get reference stars from VizieR
    
    Parameters:
    -----------
    image_header : astropy.io.fits.Header
        FITS header containing WCS information
    radius : astropy.units.Quantity
        Search radius around image center
    catalog : str
        VizieR catalog identifier
    
    Returns:
    --------
    astropy.table.Table
        Table of reference stars
    """
    # Get WCS from header
    try:
        w = WCS(image_header)
    except Exception as e:
        raise ValueError(f"Could not create WCS: {e}")
    
    # Get image center coordinates
    center_pixels = np.array([[w.pixel_shape[0]/2, w.pixel_shape[1]/2]])
    center_world = w.pixel_to_world(center_pixels[:, 0], center_pixels[:, 1])
    center_coord = SkyCoord(center_world.ra[0], center_world.dec[0])
    
    # Set up Vizier query
    v = Vizier(columns=['*', '+_r'])
    v.row_limit = -1  # No row limit
    
    try:
        # Query catalog
        result = v.query_region(center_coord, radius=radius, catalog=catalog)
        
        if len(result) == 0:
            raise ValueError(f"No reference stars found in catalog {catalog}")
        
        return result[0]  # Return first table from result
    
    except Exception as e:
        raise ValueError(f"Error querying VizieR catalog: {e}")

def detect_sources(image, fwhm=4.0, threshold=5.0):
    """
    Detect sources using DAOStarFinder
    
    Parameters:
    -----------
    image : numpy.ndarray
        The processed image array
    fwhm : float
        Full-width at half-maximum of the PSF in pixels
    threshold : float
        Detection threshold in terms of standard deviations above background
    
    Returns:
    --------
    astropy.table.Table
        Table of detected sources
    """
    # Compute background statistics
    mean, median, std = sigma_clipped_stats(image)
    
    # Detect sources
    daofind = DAOStarFinder(fwhm=fwhm, threshold=threshold * std)
    sources = daofind(image - median)
    
    return sources

def perform_aperture_photometry(image, sources, aperture_radius=5.0, annulus_radii=(8.0, 12.0)):
    """
    Perform aperture photometry with background subtraction
    
    Parameters:
    -----------
    image : numpy.ndarray
        The processed image array
    sources : astropy.table.Table
        Table of detected sources
    aperture_radius : float
        Radius of the photometry aperture in pixels
    annulus_radii : tuple
        Inner and outer radii of the background annulus in pixels
    
    Returns:
    --------
    astropy.table.Table
        Photometry results table
    """
    # Convert source positions to list of x,y coordinates
    positions = np.transpose((sources['xcentroid'], sources['ycentroid']))
    
    # Create apertures
    apertures = CircularAperture(positions, r=aperture_radius)
    annulus = CircularAnnulus(positions, r_in=annulus_radii[0], r_out=annulus_radii[1])
    
    # Perform photometry
    phot_table = aperture_photometry(image, apertures)
    
    # Compute background
    annulus_masks = annulus.to_mask(method='center')
    bkg_median = []
    
    # print("LEN_ANNULUS_MASKS= \n", len(annulus_masks))
    for mask in annulus_masks:
        annulus_data = mask.multiply(image)
        if annulus_data is not None:
            annulus_data_1d = annulus_data[mask.data > 0]
            bkg_median.append(np.nanmedian(annulus_data_1d))
        else:
            bkg_median.append(0)
    
    # Subtract background
    bkg_median = np.array(bkg_median)
    bkg_sum = bkg_median * apertures.area
    # print("BKG_MEDIAN = \n", bkg_median)
    
    final_sum = phot_table['aperture_sum'] - bkg_sum
    phot_table['final_flux'] = final_sum
    
    return phot_table

def match_sources(sources, reference_stars, wcs, max_distance=2*u.arcsec):
    """
    Match detected sources with reference stars
    
    Parameters:
    -----------
    sources : astropy.table.Table
        Table of detected sources
    reference_stars : astropy.table.Table
        Table of reference stars
    wcs : astropy.wcs.WCS
        WCS solution for the image
    max_distance : astropy.units.Quantity
        Maximum matching distance
        
    Returns:
    --------
    tuple
        (matched_sources, matched_refs) - Tables of matched sources and reference stars
    """

    print("\n*** Starting Match sources *** \n")

    # Convert source pixel coordinates to sky coordinates
    source_coords = wcs.pixel_to_world(sources['xcentroid'], sources['ycentroid'])
    
    # Get reference star coordinates
    ref_coords = SkyCoord(ra=reference_stars['RAJ2000'],
                          dec=reference_stars['DEJ2000'])
    
    # Match coordinates
    idx, d2d, _ = match_coordinates_sky(source_coords, ref_coords)
    mask = d2d < max_distance
    
    # Return matched sources and references
    return sources[mask], reference_stars[idx[mask]]


def calculate_absolute_photometry(phot_table, exposure_time, zeropoint, airmass, extinction_coeff):
    """
    Calculate absolute magnitudes
    
    Parameters:
    -----------
    phot_table : astropy.table.Table
        Photometry table
    exposure_time : float
        Exposure time in seconds
    zeropoint : float
        Photometric zeropoint
    airmass : float
        Airmass of observation
    extinction_coeff : float
        Atmospheric extinction coefficient
    
    Returns:
    --------
    numpy.ndarray
        Array of absolute magnitudes
    """
    # Calculate instrumental magnitudes
    inst_mag = -2.5 * np.log10(phot_table['final_flux'] / exposure_time)
    
    # Apply extinction correction
    extinction_correction = extinction_coeff * airmass
    
    # Calculate absolute magnitudes
    abs_mag = inst_mag + zeropoint - extinction_correction
    
    return abs_mag

def calculate_statistics(phot_table):
    """
    Calculate statistics for photometric measurements
    
    Parameters:
    -----------
    phot_table : astropy.table.Table
        Photometry table
    
    Returns:
    --------
    dict
        Dictionary of statistical measurements
    """
    stats = {
        'Flux Statistics': {
            'Minimum Flux': np.nanmin(phot_table['final_flux']),
            'Maximum Flux': np.nanmax(phot_table['final_flux']),
            'Mean Flux': np.nanmean(phot_table['final_flux']),
            'Median Flux': np.nanmedian(phot_table['final_flux'])
        },
        'Magnitude Statistics': {
            'Brightest Magnitude': np.nanmin(phot_table['absolute_magnitude']),
            'Faintest Magnitude': np.nanmax(phot_table['absolute_magnitude']),
            'Mean Magnitude': np.nanmean(phot_table['absolute_magnitude']),
            'Median Magnitude': np.nanmedian(phot_table['absolute_magnitude'])
        }
    }
    return stats

def calculate_zeropoint(phot_table, matched_refs, matched_sources, filter_name='J'):
    """
    Calculate photometric zero point
    """
    try:
        # Find indices of matched sources in the original photometry table
        matched_indices = []
        
        print("=== MATCHED_PHOTO_TABLE \n", phot_table.colnames)
        # Make sure we're using the correct column names
        x_col = 'xcenter' if 'xcenter' in phot_table.colnames else 'xcentroid'
        y_col = 'ycenter' if 'ycenter' in phot_table.colnames else 'ycentroid'
        
        print("Nro. Matched sources: \n", len(matched_sources))
        print("Nro. Photo_table: \n", len(phot_table))
        for i,matched_source in enumerate(matched_sources):
            # Match based on x and y coordinates with small tolerance
            mask = (np.abs(phot_table[x_col][i].value - matched_source['xcentroid']) < 1e-6) & \
                   (np.abs(phot_table[y_col][i].value - matched_source['ycentroid']) < 1e-6)
            if mask:
                matched_indices.append(True)
        
        print("MATCHED_INDICES=", matched_indices)

        if not matched_indices:
            raise ValueError("No matching sources found")
            
        # Get fluxes only for matched sources
        matched_fluxes = phot_table['final_flux'][matched_indices]
        
        # Check for valid fluxes
        if np.any(matched_fluxes <= 0):
            raise ValueError("Invalid (zero or negative) fluxes found")
            
        # Calculate instrumental magnitudes
        inst_mag = -2.5 * np.log10(matched_fluxes)
        print("INST_MAG\n", inst_mag)

        # Get reference magnitudes based on filter
        print("FILTER ---> ", filter_name)
        ref_mag_column = {
            'J': 'Jmag',
            'H': 'Hmag',
            'K': 'Kmag',
            'KS': 'Kmag'
        }.get(filter_name.upper(), 'Jmag')
        
        if ref_mag_column not in matched_refs.colnames:
            raise ValueError(f"Reference magnitude column {ref_mag_column} not found")
            
        ref_mag = matched_refs[ref_mag_column]
        print("REF_MAG\n", ref_mag)
        
        # Verify shapes match
        if len(ref_mag) != len(inst_mag):
            raise ValueError(f"Magnitude arrays do not match: {len(ref_mag)} vs {len(inst_mag)}")
        
        # Calculate zero points
        zeropoints = ref_mag - inst_mag
        
        print("Zero points=\n", zeropoints)
        # Sigma clipping
        median_zp = np.nanmedian(zeropoints)
        std_zp = np.nanstd(zeropoints)
        print(f"Median ZP: {median_zp:.3f}")
        print(f"Std ZP: {std_zp:.3f}")

        good_zp = np.abs(zeropoints - median_zp) < 3 * std_zp
        
        if not np.any(good_zp):
            raise ValueError("No good zeropoints found after sigma clipping")
        
        # Final zero point calculation
        final_zp = np.median(zeropoints[good_zp])
        final_std = np.std(zeropoints[good_zp])
        
        print(f"\nZero point calculation:")
        print(f"Total matched stars: {len(inst_mag)}")
        print(f"Stars after sigma clipping: {np.sum(good_zp)}")
        print(f"Zero point: {final_zp:.3f} ± {final_std:.3f} mag")
        
        return final_zp, final_std
        
    except Exception as e:
        print(f"Error in zeropoint calculation: {str(e)}")
        return None, None

def main(args):
    """
    Main photometry processing function
    """
    try:
        # Suppress certain warnings
        warnings.filterwarnings('ignore', category=RuntimeWarning)
        
        # Read image and header
        with fits.open(args.image) as hdul:
            image = hdul[0].data
            header = hdul[0].header
            try:
                h_exptime = header['EXPTIME']
                h_filter = header['FILTER'].strip()
                h_airmass = header['AIRMASS']
            except Exception as e:
                print("Some keyword (EXPTIME, FILTER, AIRMASS) is missing, user input value used")
                h_exptime = args.exptime
                h_filter = args.filter
                h_airmass = args.airmass
            else:
                print("** FILTER=%s--   EXPTIME=%s   AIRMASS=%s"%(h_filter, h_exptime, h_airmass))

        # Get WCS
        try:
            wcs = WCS(header)
        except Exception as e:
            print(f"Error reading/creating WCS: {e}")
            return None, None
        
        ######### Detect sources ##############################################
        
        sources = detect_sources(image, fwhm=args.fwhm, threshold=args.threshold)
        print("==== DETECTED SOURCES = \n ", sources)
        
        if sources is None or len(sources) == 0:
            print("No sources detected in the image!")
            return None, None
        
                
        
        ######## Zeropoint calculation  #######################################
        print("---------> Starting ZP calculation")
        zeropoint = args.zeropoint
        if args.calculate_zp:
            try:
                ######## Get reference stars
                reference_stars = get_reference_stars(
                    header, 
                    radius=args.search_radius*u.arcmin,
                    catalog=args.catalog
                )
                
                print("Catalog results ---> \n", reference_stars)

                ####### Match sources
                matched_sources, matched_refs = match_sources(
                    sources, 
                    reference_stars, 
                    wcs,
                    max_distance=args.match_distance*u.arcsec
                )
                
                print("\n====> MATCHED_SOURCES = \n", matched_sources)
                print("\n====> Matched references = \n", matched_refs)

 
                ########## Perform photometry of matched sources
                phot_table = perform_aperture_photometry(
                    image, 
                    matched_sources, 
                    aperture_radius=args.aperture,
                    annulus_radii=(args.annulus_inner, args.annulus_outer)
                )
                print("\n====> PHOTO_TABLE_OF_MATCHED= \n",phot_table)

        
                ######## Calculate zeropoint
                zp, zp_std = calculate_zeropoint(
                    phot_table, 
                    matched_refs, 
                    matched_sources, 
                    filter_name=h_filter
                )
                
                # Use calculated zeropoint if no manual zeropoint provided
                if zeropoint is None and zp is not None:
                    zeropoint = zp
            
            except Exception as e:
                print(f"Zeropoint calculation failed: {e}")
                if zeropoint is None:
                    print("No fallback zeropoint provided. Exiting.")
                    return None, None
        
        # Make sure we have a valid zeropoint before proceeding
        if zeropoint is None:
            print("No valid zeropoint available. Exiting.")
            return None, None
        
        # Absolute magnitude calculation
        absolute_mags = calculate_absolute_photometry(
            phot_table, 
            h_exptime, 
            zeropoint, 
            h_airmass, 
            args.extinction
        )
        # print("\n====> ABS_PHOTOMETRY= \n", absolute_mags)    
        
        # Add magnitudes to photometry table
        phot_table['absolute_magnitude'] = absolute_mags
        
        # Calculate statistics
        stats = calculate_statistics(phot_table)
        
        # Save or print results
        if args.output:
            phot_table.write(f"{args.output}_photometry.txt", format='ascii', overwrite=True)
            with open(f"{args.output}_statistics.txt", 'w') as f:
                f.write("=== Photometry Statistics ===\n\n")
                f.write(f"Zeropoint_{h_filter}: {zeropoint:.3f} mag\n")
                f.write(f"Airmass: {h_airmass: .3f}\n\n")
                for category, values in stats.items():
                    f.write(f"{category}:\n\n\n")
                    for key, value in values.items():
                        f.write(f"{key}: {value:.2f}\n")
        else:
            print("\nPhotometry Results:")
            print(phot_table)
            print("\nStatistics:")
            for category, values in stats.items():
                print(f"\n{category}:")
                for key, value in values.items():
                    print(f"{key}: {value:.2f}")
        
        return phot_table, sources
        
    except Exception as e:
        print(f"Error in main function: {str(e)}")
        return None, None


def cli():
    """
    Command-line interface for the photometry script
    """
    parser = argparse.ArgumentParser(description='NIR Absolute Photometry Pipeline')
    
    # Required arguments
    parser.add_argument('image', help='Path to the processed FITS image file')
    parser.add_argument('--exptime', type=float, required=False,
                        help='Exposure time in seconds')
    parser.add_argument('--airmass', type=float, required=False,
                        help='Airmass of the observation')
    
    # Zeropoint related arguments
    parser.add_argument('--zeropoint', type=float,
                        help='Manual photometric zeropoint in magnitudes')
    parser.add_argument('--catalog', default='II/246',
                       help='VizieR catalog ID (default: II/246 for 2MASS)')
    parser.add_argument('--filter', default='J',
                       help='Filter name (default: J)')
    parser.add_argument('--search-radius', type=float, default=10,
                       help='Search radius in arcminutes (default: 10)')
    parser.add_argument('--match-distance', type=float, default=2,
                       help='Maximum matching distance in arcseconds (default: 2)')
    parser.add_argument('--calculate-zp', action='store_true',
                       help='Calculate zero point using reference catalog')

    # Other optional arguments
    parser.add_argument('--extinction', type=float, default=0.1,
                       help='Atmospheric extinction coefficient (default: 0.10)')
    parser.add_argument('--fwhm', type=float, default=3.0,
                       help='FWHM for source detection in pixels (default: 4.0)')
    parser.add_argument('--threshold', type=float, default=4.0,
                       help='Detection threshold in sigma (default: 5.0)')
    parser.add_argument('--aperture', type=float, default=5.0,
                       help='Aperture radius in pixels (default: 5.0)')
    parser.add_argument('--annulus-inner', type=float, default=8.0,
                       help='Inner radius of background annulus in pixels (default: 8.0)')
    parser.add_argument('--annulus-outer', type=float, default=12.0,
                       help='Outer radius of background annulus in pixels (default: 12.0)')

    
    parser.add_argument('--output', help='Output file prefix (optional)')
    

    return parser


# ==================================================================================
if __name__ == "__main__":

    parser = cli()
    args = parser.parse_args()
    try:
        results, sources = main(args)
        if results is None:
            sys.exit(1)
    except Exception as e:
        print(f"Error running script: {str(e)}")
        sys.exit(1)
