################################################################
# Logfile for PANIC scripts
################################################################

# 03/04/2014
############
# Create sigma-clipped median data from first focus cycle
run p_03_Focus1_medianclip.py 1
run p_03_Focus1_medianclip.py 2
run p_03_Focus1_medianclip.py 3

# Determine saturation levels
run p_04_Focus1_saturation.py 1
run p_04_Focus1_saturation.py 2
run p_04_Focus1_saturation.py 3

# 04/04/2014
############
# Re-create saturation level plot, file and low QE map
run p_04_Focus1_saturation.py 1
run p_04_Focus1_saturation.py 2
run p_04_Focus1_saturation.py 3
run p_04_Focus1_saturation.py 4
# Re-create saturation level with 95% of max
run p_04_Focus1_saturation.py 2
run p_04_Focus1_saturation.py 3

# 08/04/2014
############
# Create dark current and hot pixel map
run p_05_Focus1_dark.py 1
run p_05_Focus1_dark.py 2

# 10/04/2014
############
# Re-create saturation level file
run p_04_Focus1_saturation.py 2

# Create flatfield and bad flatfield map
run p_06_Focus1_flat.py 1
run p_06_Focus1_flat.py 2

# 11/04/2014
############
# Process focus exposures
run p_07_Focus1_scidata.py 1
run p_07_Focus1_scidata.py 2
run p_07_Focus1_scidata.py 3
run p_07_Focus1_scidata.py 4
run p_07_Focus1_scidata.py 5

# Re-create bad flatfield map
run p_06_Focus1_flat.py 2
# Re-Process focus exposures: bad flatfield mask
run p_07_Focus1_scidata.py 5

# 28/04/2014
############
# Create sigma-clipped median noise data
run p_03_Focus1_medianclip.py 4
# Create sigma-clipped median single frames flat
run p_03_Focus1_medianclip.py 5
run p_03_Focus1_medianclip.py 6

# 29/04/2014
############
# Create sigma-clipped median single frames noise
run p_03_Focus1_medianclip.py 7
run p_03_Focus1_medianclip.py 8

# Extract and plot reset levels
run p_08_Focus1_resetdrift.py 1
run p_08_Focus1_resetdrift.py 2

# 30/04/2014
############
# Create flat frame cube and analyze inflationary pixels
run p_09_Focus1_inflationpix.py 1
run p_09_Focus1_inflationpix.py 2

# Re-create sigma-clipped median single frames flat 2nd exposure
run p_03_Focus1_medianclip.py 5
run p_03_Focus1_medianclip.py 6
cd output/03_Focus1_medianclip/
rm DET_FLAT_02_SINGLE_1st_medclip0051-0059.fits
rm DET_FLAT_02_SINGLE_last_medclip0052-0060.fits

# Re-extract and plot reset levels
run p_08_Focus1_resetdrift.py 1
run p_08_Focus1_resetdrift.py 2

# Create flat lisrr frame cube
run p_09_Focus1_inflationpix.py 1
# Time series from flats
run p_09_Focus1_inflationpix.py 3

# 02/05/2014
############
# Create sigma-clipped median dark lir data
run p_03_Focus1_medianclip.py 1
# Re-create flat lisrr frame cube
run p_09_Focus1_inflationpix.py 1
# Plot data
run p_09_Focus1_inflationpix.py 4

# 14/05/2014
############
# Create sigma-clipped median data from second focus cycle
# DARK images
run p_10_Focus2_medianclip.py 1
# FLAT images
run p_10_Focus2_medianclip.py 2
# FOCUS pinhole images
run p_10_Focus2_medianclip.py 3
# NOISE images
run p_10_Focus2_medianclip.py 4

# Determine saturation level rrr-mpia
run p_11_Focus2_saturation.py 1
run p_11_Focus2_saturation.py 2
run p_11_Focus2_saturation.py 3
run p_11_Focus2_saturation.py 4

# Create dark current map and hot mask
run p_13_Focus2_dark.py 1
run p_13_Focus2_dark.py 2

# Create inflationary pixel map
run p_12_Focus2_inflationpix.py

# Create master flat and bad flatfield map
run p_14_Focus2_flat.py 1
run p_14_Focus2_flat.py 2

# 15/05/2014
############
# Process focus data in simple way
run p_15_Focus2_focus_simple.py 1
run p_15_Focus2_focus_simple.py 2
run p_15_Focus2_focus_simple.py 3

# 16/05/2014
############
# Plot filter transmission all combined
run p_16_Filter_transmission.py 1
mv output/16_Filter_transmission/All_inband.* ~/work/PANIC/Optics/Filter/Transmission/

# 20/05/2014
############
# Plot Focus 1 fit PF SG1
un p_17_Focus1_fit.py 1

# 21/05/2014
############
# hot and super hot maps
run p_18_Focus2_noisedata.py 1
# Noise data: Readnoise map and histograms
run p_18_Focus2_noisedata.py 2
run p_18_Focus2_noisedata.py 3

# Focus 1: hot and super hot maps
run p_19_Focus1_noisedata.py 1
# Noise data: Readnoise map and histograms
run p_19_Focus1_noisedata.py 2
run p_19_Focus1_noisedata.py 3

# Focus 2: Repeat noise data: Readnoise map and histograms
run p_18_Focus2_noisedata.py 2
run p_18_Focus2_noisedata.py 3

# 22/05/2014
############
# Focus 2: median clip dark cubes
run p_10_Focus2_medianclip.py 5

# 22/05/2014
############
# Noise data: warm map and readnoise with Gauss
run p_18_Focus2_noisedata.py 1
run p_18_Focus2_noisedata.py 3
run p_19_Focus2_noisedata.py 1
run p_19_Focus2_noisedata.py 3

# 25/05/2014
############
# Noise data: new gain values for April/May 2014
run p_18_Focus2_noisedata.py 1
run p_18_Focus2_noisedata.py 2
run p_18_Focus2_noisedata.py 3
run p_19_Focus2_noisedata.py 1
run p_19_Focus2_noisedata.py 2
run p_19_Focus2_noisedata.py 3

# Dark cube: polynomial fit, histograms, ramps
run p_20_Focus2_darkcube.py 1
run p_20_Focus2_darkcube.py 2
run p_20_Focus2_darkcube.py 3
run p_20_Focus2_darkcube.py 4

# 27/05/2014
############
# Noise data: lir
run p_18_Focus2_noisedata.py 1 lir
run p_18_Focus2_noisedata.py 2 lir
run p_18_Focus2_noisedata.py 3 lir
run p_19_Focus1_noisedata.py 1 lir
run p_19_Focus1_noisedata.py 2 lir
run p_19_Focus1_noisedata.py 3 lir

# Median clip of old darks
run p_21_Old_medianclip.py 1
run p_21_Old_medianclip.py 2
run p_21_Old_medianclip.py 3
run p_21_Old_medianclip.py 4

# Old noise data: hot pixels
run p_22_Old_noisedata.py 1 1
run p_22_Old_noisedata.py 1 2
run p_22_Old_noisedata.py 1 3
run p_22_Old_noisedata.py 1 4

# 03/06/2014
############
# Focus 2a medial clip focus data
run p_23_Focus2a_medianclip.py 1
run p_23_Focus2a_medianclip.py 2
run p_23_Focus2a_medianclip.py 3

# Focus 2a focus images
run p_24_Focus2a_focus_simple.py 1
run p_24_Focus2a_focus_simple.py 2
run p_24_Focus2a_focus_simple.py 3

# Focus 2 medial clip dark singles
run p_10_Focus2_medianclip.py 6
run p_10_Focus2_medianclip.py 7

# 04/06/14
############
# Reset level analysis
run p_25_Focus2_resetdrift.py 1
run p_25_Focus2_resetdrift.py 2

# 11/06/14
############
# Nonlinearity correction concept rrr-mpia and lir
run p_26_linearity_test.py 1
run p_26_linearity_test.py 2

# 30/06/14
############
# Nonlinearity correction concept 2 rrr-mpia and lir
run p_27_linearity_test_2.py lir 1
run p_27_linearity_test_2.py lir 2
run p_27_linearity_test_2.py lir 3
run p_27_linearity_test_2.py rrr-mpia 1
run p_27_linearity_test_2.py rrr-mpia 2
run p_27_linearity_test_2.py rrr-mpia 3

# 01/07/14
############
# Idle mode data
run p_28_Focus2_idlemode.py 1
run p_28_Focus2_idlemode.py 2
# Focus 2a flatfields
run p_23_Focus2a_medianclip.py 4

# 02/07/14
############
# Nonlinearity correction concept 2 with 2a data rrr-mpia and lir
run p_27_linearity_test_2.py rrr-mpia 1
run p_27_linearity_test_2.py rrr-mpia 2
run p_27_linearity_test_2.py rrr-mpia 3
run p_27_linearity_test_2.py lir 1
run p_27_linearity_test_2.py lir 2
run p_27_linearity_test_2.py lir 3

# Median clip nosie data 2a
run p_23_Focus2a_medianclip.py 5

# 03/07/14
############
# Median clip linearity test data 2a
run p_23_Focus2a_medianclip.py 6

# Nonlinearity correction data
run p_29_nonlinearity_data.py rrr-mpia 1
run p_29_nonlinearity_data.py lir 1
run p_29_nonlinearity_data.py rrr-mpia 2
run p_29_nonlinearity_data.py lir 2
run p_29_nonlinearity_data.py rrr-mpia 3
run p_29_nonlinearity_data.py lir 3

# 04/07/14
############
# Plot nonlinearity correction data
run p_29_nonlinearity_data.py rrr-mpia 4
run p_29_nonlinearity_data.py lir 4

# Test cutoff for nonlinearity
run p_27_linearity_test_2.py lir 1
run p_27_linearity_test_2.py lir 2
run p_27_linearity_test_2.py lir 3

# Plot more nonlinearity correction data
run p_29_nonlinearity_data.py rrr-mpia 4
run p_29_nonlinearity_data.py lir 4

# Refit nonlinearity correction and plot
run p_29_nonlinearity_data.py rrr-mpia 3
run p_29_nonlinearity_data.py lir 3
run p_29_nonlinearity_data.py lir 4
run p_29_nonlinearity_data.py rrr-mpia 4

# Plot nonlinearity correction data again
run p_29_nonlinearity_data.py rrr-mpia 4
run p_29_nonlinearity_data.py lir 4

# Refit nonlinearity correction and plot
run p_29_nonlinearity_data.py rrr-mpia 3
run p_29_nonlinearity_data.py lir 3
run p_29_nonlinearity_data.py lir 4
run p_29_nonlinearity_data.py rrr-mpia 4

# 07/07/14
############
# Refit nonlinearity correction and plot
run p_29_nonlinearity_data.py rrr-mpia 3
run p_29_nonlinearity_data.py lir 3
run p_29_nonlinearity_data.py rrr-mpia 4
run p_29_nonlinearity_data.py lir 4

# Refit nonlinearity correction and plot
run p_29_nonlinearity_data.py rrr-mpia 3
run p_29_nonlinearity_data.py lir 3
run p_29_nonlinearity_data.py rrr-mpia 4
run p_29_nonlinearity_data.py lir 4

# 08/07/14
############
# Test nonlinearity with other illumination
run p_30_test_nonlinearity.py rrr-mpia 1 all
run p_30_test_nonlinearity.py rrr-mpia 2 all
run p_30_test_nonlinearity.py rrr-mpia 3 all
run p_30_test_nonlinearity.py rrr-mpia 4 all
run p_30_test_nonlinearity.py rrr-mpia 5 all
run p_30_test_nonlinearity.py lir 1 all
run p_30_test_nonlinearity.py lir 2 all
run p_30_test_nonlinearity.py lir 3 all
run p_30_test_nonlinearity.py lir 4 all
run p_30_test_nonlinearity.py lir 5 all

# Median clip focus data third iteration
run p_31_Focus3_medianclip.py 1
run p_31_Focus3_medianclip.py 2
run p_31_Focus3_medianclip.py 3

# Process focus data
run p_32_Focus3_focus_simple.py 1
run p_32_Focus3_focus_simple.py 2
run p_32_Focus3_focus_simple.py 3

# 09/07/14
############
# Write nonlinearity data in MEF format and with new headers
run p_29_nonlinearity_data.py rrr-mpia 5
run p_29_nonlinearity_data.py lir 5

# 10/07/14
############
# Write nonlinearity data in MEF format and with new headers
run p_29_nonlinearity_data.py rrr-mpia 5
run p_29_nonlinearity_data.py lir 5

# 11/07/14
############
# Test idle mode type Rlr
run p_33_Focus3_idlemode.py lir 1
run p_33_Focus3_idlemode.py lir 2
run p_33_Focus3_idlemode.py rrr-mpia 1
run p_33_Focus3_idlemode.py rrr-mpia 2

# 14/07/14
############
# Write nonlinearity data in MEF format and with new headers
run p_29_nonlinearity_data.py rrr-mpia 5
run p_29_nonlinearity_data.py lir 5

# Noise data: Focus 2a
run p_34_Focus2a_noisedata.py 1 lir
run p_34_Focus2a_noisedata.py 2 lir
run p_34_Focus2a_noisedata.py 3 lir
run p_34_Focus2a_noisedata.py 1 rrr-mpia
run p_34_Focus2a_noisedata.py 2 rrr-mpia
run p_34_Focus2a_noisedata.py 3 rrr-mpia

# Median clip Focus 3 noise data
run p_31_Focus3_medianclip.py 4

# Noise data: Focus 3
run p_35_Focus3_noisedata.py 1 lir
run p_35_Focus3_noisedata.py 2 lir
run p_35_Focus3_noisedata.py 3 lir
run p_35_Focus3_noisedata.py 1 rrr-mpia
run p_35_Focus3_noisedata.py 2 rrr-mpia
run p_35_Focus3_noisedata.py 3 rrr-mpia

# 15/07/14
############
# Create max. nonlinear correction images
run p_29_nonlinearity_data.py rrr-mpia 6
run p_29_nonlinearity_data.py lir 6

# 17/07/14
############
# Focus 2: saturation data lir
run p_11_Focus2_saturation.py 1 lir
run p_11_Focus2_saturation.py 2 lir

# 28/07/14
############
# Focus 2: low QE data lir
run p_11_Focus2_saturation.py 4 lir

# 29/07/14
############
# Median clip nosie data cycle 5
run p_36_cyc5_medianclip.py 1

# 01/08/14
############
# Cycle 5 noise data
run p_37_cyc5_noisedata.py 1 rrr-mpia
run p_37_cyc5_noisedata.py 2 rrr-mpia
run p_37_cyc5_noisedata.py 3 rrr-mpia
run p_37_cyc5_noisedata.py 1 lir
run p_37_cyc5_noisedata.py 2 lir
run p_37_cyc5_noisedata.py 3 lir

# 14/08/2014
##############
# Plot SS tilt FWHM data
run p_38_SS1_tilt.py 1

# 15/08/2014
##############
# Median clip 2nd noise data cycle 5
run p_36_cyc5_medianclip.py 2
# Median clip flatfield CDS
run p_36_cyc5_medianclip.py 3

# 27/08/14
############
# Cycle 5 2nd noise data
run p_39_cyc5_noisedata2.py 1 rrr-mpia
run p_39_cyc5_noisedata2.py 2 rrr-mpia
run p_39_cyc5_noisedata2.py 3 rrr-mpia
run p_39_cyc5_noisedata2.py 1 lir
run p_39_cyc5_noisedata2.py 2 lir
run p_39_cyc5_noisedata2.py 3 lir

# 06/10/14
##########
# Move detector data to data repository and create symlink
# 04
mv output/04_Focus1_saturation/LowQE_lir_0001.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/LowQE_lir_0001.fits output/04_Focus1_saturation/LowQE_lir_0001.fits
mv output/04_Focus1_saturation/Satlevel_lir_CDS_0001.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Satlevel_lir_CDS_0001.fits output/04_Focus1_saturation/Satlevel_lir_CDS_0001.fits
# 05
mv output/05_Focus1_dark/Dark_lir_0001.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Dark_lir_0001.fits output/05_Focus1_dark/Dark_lir_0001.fits
mv output/05_Focus1_dark/Hot_lir_0001.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_lir_0001.fits output/05_Focus1_dark/Hot_lir_0001.fits
# 06
mv output/06_Focus1_flat/BadFF_lir_0001.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/BadFF_lir_0001.fits output/06_Focus1_flat/BadFF_lir_0001.fits
mv output/06_Focus1_flat/Flat_lir_0001.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Flat_lir_0001.fits output/06_Focus1_flat/Flat_lir_0001.fits
# 09
mv output/09_Focus1_inflationpix/Inflpix_srr_0001.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Inflpix_srr_0001.fits output/09_Focus1_inflationpix/Inflpix_srr_0001.fits
# 11
mv output/11_Focus2_saturation/Cold_lir_0002.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Cold_lir_0002.fits output/11_Focus2_saturation/Cold_lir_0002.fits
mv output/11_Focus2_saturation/Cold_rrr-mpia_0002.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Cold_rrr-mpia_0002.fits output/11_Focus2_saturation/Cold_rrr-mpia_0002.fits
mv output/11_Focus2_saturation/Satlevel_rrr-mpia_CDS_0002.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Satlevel_rrr-mpia_CDS_0002.fits output/11_Focus2_saturation/Satlevel_rrr-mpia_CDS_0002.fits
# 12
mv output/12_Focus2_inflationpix/Inflation_rrr-mpia_0002.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Inflation_rrr-mpia_0002.fits output/12_Focus2_inflationpix/Inflation_rrr-mpia_0002.fits
# 13
mv output/13_Focus2_dark/Dark_rrr-mpia_0002.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Dark_rrr-mpia_0002.fits output/13_Focus2_dark/Dark_rrr-mpia_0002.fits
mv output/13_Focus2_dark/Hot_rrr-mpia_0002.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0002.fits output/13_Focus2_dark/Hot_rrr-mpia_0002.fits
# 14
mv output/14_Focus2_flat/Flat_rrr-mpia_0002.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Flat_rrr-mpia_0002.fits output/14_Focus2_flat/Flat_rrr-mpia_0002.fits
mv output/14_Focus2_flat/BadFF_rrr-mpia_0002.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/BadFF_rrr-mpia_0002.fits output/14_Focus2_flat/BadFF_rrr-mpia_0002.fits

# Correct p_19_Focus1_noisedata output filenames in code and folder

# Continue moving detector data to data repository and create symlink
# 18
mv output/18_Focus2_noisedata/Hot_lir_0003.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_lir_0003.fits output/18_Focus2_noisedata/Hot_lir_0003.fits
mv output/18_Focus2_noisedata/Hot_rrr-mpia_0003.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0003.fits output/18_Focus2_noisedata/Hot_rrr-mpia_0003.fits
mv output/18_Focus2_noisedata/Noise_lir_0003.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_lir_0003.fits output/18_Focus2_noisedata/Noise_lir_0003.fits
mv output/18_Focus2_noisedata/Noise_rrr-mpia_0003.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_rrr-mpia_0003.fits output/18_Focus2_noisedata/Noise_rrr-mpia_0003.fits
mv output/18_Focus2_noisedata/Superhot_lir_0003.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_lir_0003.fits output/18_Focus2_noisedata/Superhot_lir_0003.fits
mv output/18_Focus2_noisedata/Superhot_rrr-mpia_0003.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_rrr-mpia_0003.fits output/18_Focus2_noisedata/Superhot_rrr-mpia_0003.fits
mv output/18_Focus2_noisedata/Warm_lir_0003.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_lir_0003.fits output/18_Focus2_noisedata/Warm_lir_0003.fits
mv output/18_Focus2_noisedata/Warm_rrr-mpia_0003.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_rrr-mpia_0003.fits output/18_Focus2_noisedata/Warm_rrr-mpia_0003.fits

# 07/10/14
##########
# 19
mv output/19_Focus1_noisedata/Hot_lir_0001.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_lir_0001.fits output/19_Focus1_noisedata/Hot_lir_0001.fits
mv output/19_Focus1_noisedata/Noise_lir_0001.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_lir_0001.fits output/19_Focus1_noisedata/Noise_lir_0001.fits
mv output/19_Focus1_noisedata/Superhot_lir_0001.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_lir_0001.fits output/19_Focus1_noisedata/Superhot_lir_0001.fits
mv output/19_Focus1_noisedata/Warm_lir_0001.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_lir_0001.fits output/19_Focus1_noisedata/Warm_lir_0001.fits
mv output/19_Focus1_noisedata/Hot_rrr-mpia_0001.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0001.fits output/19_Focus1_noisedata/Hot_rrr-mpia_0001.fits
mv output/19_Focus1_noisedata/Noise_rrr-mpia_0001.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_rrr-mpia_0001.fits output/19_Focus1_noisedata/Noise_rrr-mpia_0001.fits
mv output/19_Focus1_noisedata/Superhot_rrr-mpia_0001.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_rrr-mpia_0001.fits output/19_Focus1_noisedata/Superhot_rrr-mpia_0001.fits
mv output/19_Focus1_noisedata/Warm_rrr-mpia_0001.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_rrr-mpia_0001.fits output/19_Focus1_noisedata/Warm_rrr-mpia_0001.fits
# 20
mv output/20_Focus2_darkcube/Dark_rrr-mpia_0003.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Dark_rrr-mpia_0003.fits output/20_Focus2_darkcube/Dark_rrr-mpia_0003.fits
mv output/20_Focus2_darkcube/Darkpoly_rrr-mpia_0003.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Darkpoly_rrr-mpia_0003.fits output/20_Focus2_darkcube/Darkpoly_rrr-mpia_0003.fits
# 22
mv output/22_Old_noisedata/Hot_2011-12-08_lir.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_2011-12-08_lir.fits output/22_Old_noisedata/Hot_2011-12-08_lir.fits
mv output/22_Old_noisedata/Hot_2012-01-30_lir.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_2012-01-30_lir.fits output/22_Old_noisedata/Hot_2012-01-30_lir.fits
mv output/22_Old_noisedata/Hot_2012-11-21_lir.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_2012-11-21_lir.fits output/22_Old_noisedata/Hot_2012-11-21_lir.fits
mv output/22_Old_noisedata/Hot_2013-10-04_lir.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_2013-10-04_lir.fits output/22_Old_noisedata/Hot_2013-10-04_lir.fits
mv output/22_Old_noisedata/Superhot_2011-12-08_lir.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_2011-12-08_lir.fits output/22_Old_noisedata/Superhot_2011-12-08_lir.fits
mv output/22_Old_noisedata/Superhot_2012-01-30_lir.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_2012-01-30_lir.fits output/22_Old_noisedata/Superhot_2012-01-30_lir.fits
mv output/22_Old_noisedata/Superhot_2012-11-21_lir.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_2012-11-21_lir.fits output/22_Old_noisedata/Superhot_2012-11-21_lir.fits
mv output/22_Old_noisedata/Superhot_2013-10-04_lir.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_2013-10-04_lir.fits output/22_Old_noisedata/Superhot_2013-10-04_lir.fits
mv output/22_Old_noisedata/Warm_2011-12-08_lir.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_2011-12-08_lir.fits output/22_Old_noisedata/Warm_2011-12-08_lir.fits
mv output/22_Old_noisedata/Warm_2012-01-30_lir.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_2012-01-30_lir.fits output/22_Old_noisedata/Warm_2012-01-30_lir.fits
mv output/22_Old_noisedata/Warm_2012-11-21_lir.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_2012-11-21_lir.fits output/22_Old_noisedata/Warm_2012-11-21_lir.fits
mv output/22_Old_noisedata/Warm_2013-10-04_lir.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_2013-10-04_lir.fits output/22_Old_noisedata/Warm_2013-10-04_lir.fits
# 29
mv output/29_nonlinearity_data_lir/NONLIN_LIR_0001.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/NONLIN_LIR_0001.fits output/29_nonlinearity_data_lir/NONLIN_LIR_0001.fits
mv output/29_nonlinearity_data_lir/mNONLIN_LIR_00.01.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/mNONLIN_LIR_00.01.fits output/29_nonlinearity_data_lir/mNONLIN_LIR_00.01.fits
mv output/29_nonlinearity_data_rrr-mpia/NONLIN_RRR-MPIA_0001.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/NONLIN_RRR-MPIA_0001.fits output/29_nonlinearity_data_rrr-mpia/NONLIN_RRR-MPIA_0001.fits
mv output/29_nonlinearity_data_rrr-mpia/mNONLIN_RRR-MPIA_00.01.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/mNONLIN_RRR-MPIA_00.01.fits output/29_nonlinearity_data_rrr-mpia/mNONLIN_RRR-MPIA_00.01.fits
# 34
mv output/34_Focus2a_noisedata/Hot_lir_0004.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_lir_0004.fits output/34_Focus2a_noisedata/Hot_lir_0004.fits
mv output/34_Focus2a_noisedata/Noise_lir_0004.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_lir_0004.fits output/34_Focus2a_noisedata/Noise_lir_0004.fits
mv output/34_Focus2a_noisedata/Superhot_lir_0004.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_lir_0004.fits output/34_Focus2a_noisedata/Superhot_lir_0004.fits
mv output/34_Focus2a_noisedata/Warm_lir_0004.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_lir_0004.fits output/34_Focus2a_noisedata/Warm_lir_0004.fits
mv output/34_Focus2a_noisedata/Hot_rrr-mpia_0004.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0004.fits output/34_Focus2a_noisedata/Hot_rrr-mpia_0004.fits
mv output/34_Focus2a_noisedata/Noise_rrr-mpia_0004.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_rrr-mpia_0004.fits output/34_Focus2a_noisedata/Noise_rrr-mpia_0004.fits
mv output/34_Focus2a_noisedata/Superhot_rrr-mpia_0004.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_rrr-mpia_0004.fits output/34_Focus2a_noisedata/Superhot_rrr-mpia_0004.fits
mv output/34_Focus2a_noisedata/Warm_rrr-mpia_0004.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_rrr-mpia_0004.fits output/34_Focus2a_noisedata/Warm_rrr-mpia_0004.fits
# 35
mv output/35_Focus3_noisedata/Hot_lir_0005.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_lir_0005.fits output/35_Focus3_noisedata/Hot_lir_0005.fits
mv output/35_Focus3_noisedata/Noise_lir_0005.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_lir_0005.fits output/35_Focus3_noisedata/Noise_lir_0005.fits
mv output/35_Focus3_noisedata/Superhot_lir_0005.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_lir_0005.fits output/35_Focus3_noisedata/Superhot_lir_0005.fits
mv output/35_Focus3_noisedata/Warm_lir_0005.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_lir_0005.fits output/35_Focus3_noisedata/Warm_lir_0005.fits
mv output/35_Focus3_noisedata/Hot_rrr-mpia_0005.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0005.fits output/35_Focus3_noisedata/Hot_rrr-mpia_0005.fits
mv output/35_Focus3_noisedata/Noise_rrr-mpia_0005.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_rrr-mpia_0005.fits output/35_Focus3_noisedata/Noise_rrr-mpia_0005.fits
mv output/35_Focus3_noisedata/Superhot_rrr-mpia_0005.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_rrr-mpia_0005.fits output/35_Focus3_noisedata/Superhot_rrr-mpia_0005.fits
mv output/35_Focus3_noisedata/Warm_rrr-mpia_0005.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_rrr-mpia_0005.fits output/35_Focus3_noisedata/Warm_rrr-mpia_0005.fits
# 37
mv output/37_cyc5_noisedata/Hot_lir_0006.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_lir_0006.fits output/37_cyc5_noisedata/Hot_lir_0006.fits
mv output/37_cyc5_noisedata/Noise_lir_0006.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_lir_0006.fits output/37_cyc5_noisedata/Noise_lir_0006.fits
mv output/37_cyc5_noisedata/Superhot_lir_0006.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_lir_0006.fits output/37_cyc5_noisedata/Superhot_lir_0006.fits
mv output/37_cyc5_noisedata/Warm_lir_0006.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_lir_0006.fits output/37_cyc5_noisedata/Warm_lir_0006.fits
mv output/37_cyc5_noisedata/Hot_rrr-mpia_0006.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0006.fits output/37_cyc5_noisedata/Hot_rrr-mpia_0006.fits
mv output/37_cyc5_noisedata/Noise_rrr-mpia_0006.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_rrr-mpia_0006.fits output/37_cyc5_noisedata/Noise_rrr-mpia_0006.fits
mv output/37_cyc5_noisedata/Superhot_rrr-mpia_0006.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_rrr-mpia_0006.fits output/37_cyc5_noisedata/Superhot_rrr-mpia_0006.fits
mv output/37_cyc5_noisedata/Warm_rrr-mpia_0006.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_rrr-mpia_0006.fits output/37_cyc5_noisedata/Warm_rrr-mpia_0006.fits
# 39
mv output/39_cyc5_noisedata/Hot_lir_0007.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_lir_0007.fits output/39_cyc5_noisedata/Hot_lir_0007.fits
mv output/39_cyc5_noisedata/Noise_lir_0007.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_lir_0007.fits output/39_cyc5_noisedata/Noise_lir_0007.fits
mv output/39_cyc5_noisedata/Superhot_lir_0007.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_lir_0007.fits output/39_cyc5_noisedata/Superhot_lir_0007.fits
mv output/39_cyc5_noisedata/Warm_lir_0007.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_lir_0007.fits output/39_cyc5_noisedata/Warm_lir_0007.fits
mv output/39_cyc5_noisedata/Hot_rrr-mpia_0007.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0007.fits output/39_cyc5_noisedata/Hot_rrr-mpia_0007.fits
mv output/39_cyc5_noisedata/Noise_rrr-mpia_0007.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_rrr-mpia_0007.fits output/39_cyc5_noisedata/Noise_rrr-mpia_0007.fits
mv output/39_cyc5_noisedata/Superhot_rrr-mpia_0007.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_rrr-mpia_0007.fits output/39_cyc5_noisedata/Superhot_rrr-mpia_0007.fits
mv output/39_cyc5_noisedata/Warm_rrr-mpia_0007.fits data/Detector/Calibration/
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_rrr-mpia_0007.fits output/39_cyc5_noisedata/Warm_rrr-mpia_0007.fits

# Synchronize data with aida43216
sync_PANICdata.sh

# Re-create noise data for 2014 cycles with corrections
# cycle 1
run p_19_Focus1_noisedata.py 1 lir
run p_19_Focus1_noisedata.py 2 lir
run p_19_Focus1_noisedata.py 3 lir
run p_19_Focus1_noisedata.py 1 rrr-mpia
run p_19_Focus1_noisedata.py 2 rrr-mpia
run p_19_Focus1_noisedata.py 3 rrr-mpia
# Move output data to repository
mv output/19_Focus1_noisedata/Hot_lir_0001.fits data/Detector/Calibration/
mv output/19_Focus1_noisedata/Noise_lir_0001.fits data/Detector/Calibration/
mv output/19_Focus1_noisedata/Superhot_lir_0001.fits data/Detector/Calibration/
mv output/19_Focus1_noisedata/Warm_lir_0001.fits data/Detector/Calibration/
mv output/19_Focus1_noisedata/Hot_rrr-mpia_0001.fits data/Detector/Calibration/
mv output/19_Focus1_noisedata/Noise_rrr-mpia_0001.fits data/Detector/Calibration/
mv output/19_Focus1_noisedata/Superhot_rrr-mpia_0001.fits data/Detector/Calibration/
mv output/19_Focus1_noisedata/Warm_rrr-mpia_0001.fits data/Detector/Calibration/
# copy output to other machine, then sync data and recreate symlinks
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_lir_0001.fits output/19_Focus1_noisedata/Hot_lir_0001.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_lir_0001.fits output/19_Focus1_noisedata/Noise_lir_0001.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_lir_0001.fits output/19_Focus1_noisedata/Superhot_lir_0001.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_lir_0001.fits output/19_Focus1_noisedata/Warm_lir_0001.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0001.fits output/19_Focus1_noisedata/Hot_rrr-mpia_0001.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_rrr-mpia_0001.fits output/19_Focus1_noisedata/Noise_rrr-mpia_0001.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_rrr-mpia_0001.fits output/19_Focus1_noisedata/Superhot_rrr-mpia_0001.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_rrr-mpia_0001.fits output/19_Focus1_noisedata/Warm_rrr-mpia_0001.fits

# cycle 2
run p_18_Focus2_noisedata.py 1 lir
run p_18_Focus2_noisedata.py 2 lir
run p_18_Focus2_noisedata.py 3 lir
run p_18_Focus2_noisedata.py 1 rrr-mpia
run p_18_Focus2_noisedata.py 2 rrr-mpia
run p_18_Focus2_noisedata.py 3 rrr-mpia
# Move output data to repository
mv output/18_Focus2_noisedata/Hot_lir_0003.fits data/Detector/Calibration/
mv output/18_Focus2_noisedata/Hot_rrr-mpia_0003.fits data/Detector/Calibration/
mv output/18_Focus2_noisedata/Noise_lir_0003.fits data/Detector/Calibration/
mv output/18_Focus2_noisedata/Noise_rrr-mpia_0003.fits data/Detector/Calibration/
mv output/18_Focus2_noisedata/Superhot_lir_0003.fits data/Detector/Calibration/
mv output/18_Focus2_noisedata/Superhot_rrr-mpia_0003.fits data/Detector/Calibration/
mv output/18_Focus2_noisedata/Warm_lir_0003.fits data/Detector/Calibration/
mv output/18_Focus2_noisedata/Warm_rrr-mpia_0003.fits data/Detector/Calibration/
# copy output to other machine, then sync data and recreate symlinks
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_lir_0003.fits output/18_Focus2_noisedata/Hot_lir_0003.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0003.fits output/18_Focus2_noisedata/Hot_rrr-mpia_0003.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_lir_0003.fits output/18_Focus2_noisedata/Noise_lir_0003.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_rrr-mpia_0003.fits output/18_Focus2_noisedata/Noise_rrr-mpia_0003.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_lir_0003.fits output/18_Focus2_noisedata/Superhot_lir_0003.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_rrr-mpia_0003.fits output/18_Focus2_noisedata/Superhot_rrr-mpia_0003.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_lir_0003.fits output/18_Focus2_noisedata/Warm_lir_0003.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_rrr-mpia_0003.fits output/18_Focus2_noisedata/Warm_rrr-mpia_0003.fits

# cycle 3
run p_34_Focus2a_noisedata.py 1 lir
run p_34_Focus2a_noisedata.py 2 lir
run p_34_Focus2a_noisedata.py 3 lir
run p_34_Focus2a_noisedata.py 1 rrr-mpia
run p_34_Focus2a_noisedata.py 2 rrr-mpia
run p_34_Focus2a_noisedata.py 3 rrr-mpia
# Move output data to repository
mv output/34_Focus2a_noisedata/Hot_lir_0004.fits data/Detector/Calibration/
mv output/34_Focus2a_noisedata/Noise_lir_0004.fits data/Detector/Calibration/
mv output/34_Focus2a_noisedata/Superhot_lir_0004.fits data/Detector/Calibration/
mv output/34_Focus2a_noisedata/Warm_lir_0004.fits data/Detector/Calibration/
mv output/34_Focus2a_noisedata/Hot_rrr-mpia_0004.fits data/Detector/Calibration/
mv output/34_Focus2a_noisedata/Noise_rrr-mpia_0004.fits data/Detector/Calibration/
mv output/34_Focus2a_noisedata/Superhot_rrr-mpia_0004.fits data/Detector/Calibration/
mv output/34_Focus2a_noisedata/Warm_rrr-mpia_0004.fits data/Detector/Calibration/
# copy output to other machine, then sync data and recreate symlinks
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_lir_0004.fits output/34_Focus2a_noisedata/Hot_lir_0004.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_lir_0004.fits output/34_Focus2a_noisedata/Noise_lir_0004.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_lir_0004.fits output/34_Focus2a_noisedata/Superhot_lir_0004.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_lir_0004.fits output/34_Focus2a_noisedata/Warm_lir_0004.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0004.fits output/34_Focus2a_noisedata/Hot_rrr-mpia_0004.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_rrr-mpia_0004.fits output/34_Focus2a_noisedata/Noise_rrr-mpia_0004.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_rrr-mpia_0004.fits output/34_Focus2a_noisedata/Superhot_rrr-mpia_0004.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_rrr-mpia_0004.fits output/34_Focus2a_noisedata/Warm_rrr-mpia_0004.fits

# 08/10/14
##########
# cycle 4
run p_35_Focus3_noisedata.py 1 lir
run p_35_Focus3_noisedata.py 2 lir
run p_35_Focus3_noisedata.py 3 lir
run p_35_Focus3_noisedata.py 1 rrr-mpia
run p_35_Focus3_noisedata.py 2 rrr-mpia
run p_35_Focus3_noisedata.py 3 rrr-mpia
# Move output data to repository
mv output/35_Focus3_noisedata/Hot_lir_0005.fits data/Detector/Calibration/
mv output/35_Focus3_noisedata/Noise_lir_0005.fits data/Detector/Calibration/
mv output/35_Focus3_noisedata/Superhot_lir_0005.fits data/Detector/Calibration/
mv output/35_Focus3_noisedata/Warm_lir_0005.fits data/Detector/Calibration/
mv output/35_Focus3_noisedata/Hot_rrr-mpia_0005.fits data/Detector/Calibration/
mv output/35_Focus3_noisedata/Noise_rrr-mpia_0005.fits data/Detector/Calibration/
mv output/35_Focus3_noisedata/Superhot_rrr-mpia_0005.fits data/Detector/Calibration/
mv output/35_Focus3_noisedata/Warm_rrr-mpia_0005.fits data/Detector/Calibration/
# copy output to other machine, then sync data and recreate symlinks
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_lir_0005.fits output/35_Focus3_noisedata/Hot_lir_0005.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_lir_0005.fits output/35_Focus3_noisedata/Noise_lir_0005.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_lir_0005.fits output/35_Focus3_noisedata/Superhot_lir_0005.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_lir_0005.fits output/35_Focus3_noisedata/Warm_lir_0005.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0005.fits output/35_Focus3_noisedata/Hot_rrr-mpia_0005.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_rrr-mpia_0005.fits output/35_Focus3_noisedata/Noise_rrr-mpia_0005.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_rrr-mpia_0005.fits output/35_Focus3_noisedata/Superhot_rrr-mpia_0005.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_rrr-mpia_0005.fits output/35_Focus3_noisedata/Warm_rrr-mpia_0005.fits

# Cycle 5 start
run p_37_cyc5_noisedata.py 1 lir
run p_37_cyc5_noisedata.py 2 lir
run p_37_cyc5_noisedata.py 3 lir
run p_37_cyc5_noisedata.py 1 rrr-mpia
run p_37_cyc5_noisedata.py 2 rrr-mpia
run p_37_cyc5_noisedata.py 3 rrr-mpia
# Move output data to repository
mv output/37_cyc5_noisedata/Hot_lir_0006.fits data/Detector/Calibration/
mv output/37_cyc5_noisedata/Noise_lir_0006.fits data/Detector/Calibration/
mv output/37_cyc5_noisedata/Superhot_lir_0006.fits data/Detector/Calibration/
mv output/37_cyc5_noisedata/Warm_lir_0006.fits data/Detector/Calibration/
mv output/37_cyc5_noisedata/Hot_rrr-mpia_0006.fits data/Detector/Calibration/
mv output/37_cyc5_noisedata/Noise_rrr-mpia_0006.fits data/Detector/Calibration/
mv output/37_cyc5_noisedata/Superhot_rrr-mpia_0006.fits data/Detector/Calibration/
mv output/37_cyc5_noisedata/Warm_rrr-mpia_0006.fits data/Detector/Calibration/
# copy output to other machine, then sync data and recreate symlinks
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_lir_0006.fits output/37_cyc5_noisedata/Hot_lir_0006.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_lir_0006.fits output/37_cyc5_noisedata/Noise_lir_0006.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_lir_0006.fits output/37_cyc5_noisedata/Superhot_lir_0006.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_lir_0006.fits output/37_cyc5_noisedata/Warm_lir_0006.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0006.fits output/37_cyc5_noisedata/Hot_rrr-mpia_0006.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_rrr-mpia_0006.fits output/37_cyc5_noisedata/Noise_rrr-mpia_0006.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_rrr-mpia_0006.fits output/37_cyc5_noisedata/Superhot_rrr-mpia_0006.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_rrr-mpia_0006.fits output/37_cyc5_noisedata/Warm_rrr-mpia_0006.fits

# Cycle 5 end
run p_39_cyc5_noisedata2.py 1 lir
run p_39_cyc5_noisedata2.py 2 lir
run p_39_cyc5_noisedata2.py 3 lir
run p_39_cyc5_noisedata2.py 1 rrr-mpia
run p_39_cyc5_noisedata2.py 2 rrr-mpia
run p_39_cyc5_noisedata2.py 3 rrr-mpia
# Move output data to repository
mv output/39_cyc5_noisedata/Hot_lir_0007.fits data/Detector/Calibration/
mv output/39_cyc5_noisedata/Noise_lir_0007.fits data/Detector/Calibration/
mv output/39_cyc5_noisedata/Superhot_lir_0007.fits data/Detector/Calibration/
mv output/39_cyc5_noisedata/Warm_lir_0007.fits data/Detector/Calibration/
mv output/39_cyc5_noisedata/Hot_rrr-mpia_0007.fits data/Detector/Calibration/
mv output/39_cyc5_noisedata/Noise_rrr-mpia_0007.fits data/Detector/Calibration/
mv output/39_cyc5_noisedata/Superhot_rrr-mpia_0007.fits data/Detector/Calibration/
mv output/39_cyc5_noisedata/Warm_rrr-mpia_0007.fits data/Detector/Calibration/
# copy output to other machine, then sync data and recreate symlinks
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_lir_0007.fits output/39_cyc5_noisedata/Hot_lir_0007.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_lir_0007.fits output/39_cyc5_noisedata/Noise_lir_0007.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_lir_0007.fits output/39_cyc5_noisedata/Superhot_lir_0007.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_lir_0007.fits output/39_cyc5_noisedata/Warm_lir_0007.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0007.fits output/39_cyc5_noisedata/Hot_rrr-mpia_0007.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_rrr-mpia_0007.fits output/39_cyc5_noisedata/Noise_rrr-mpia_0007.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_rrr-mpia_0007.fits output/39_cyc5_noisedata/Superhot_rrr-mpia_0007.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_rrr-mpia_0007.fits output/39_cyc5_noisedata/Warm_rrr-mpia_0007.fits

# Cycle 6: median clip noise data
run p_40_cyc6_medianclip.py 1
# Median clip flatfield CDS
run p_40_cyc6_medianclip.py 2

# 08/10/14
##########
# cycle 6: Readnoise processing
run p_41_cyc6_noisedata.py lir 1
run p_41_cyc6_noisedata.py lir 2
run p_41_cyc6_noisedata.py lir 3
run p_41_cyc6_noisedata.py rrr-mpia 1
run p_41_cyc6_noisedata.py rrr-mpia 2
run p_41_cyc6_noisedata.py rrr-mpia 3
# Move output data to repository
mv output/41_cyc6_noisedata/Hot_lir_0008.fits data/Detector/Calibration/
mv output/41_cyc6_noisedata/Noise_lir_0008.fits data/Detector/Calibration/
mv output/41_cyc6_noisedata/Superhot_lir_0008.fits data/Detector/Calibration/
mv output/41_cyc6_noisedata/Warm_lir_0008.fits data/Detector/Calibration/
mv output/41_cyc6_noisedata/Hot_rrr-mpia_0008.fits data/Detector/Calibration/
mv output/41_cyc6_noisedata/Noise_rrr-mpia_0008.fits data/Detector/Calibration/
mv output/41_cyc6_noisedata/Superhot_rrr-mpia_0008.fits data/Detector/Calibration/
mv output/41_cyc6_noisedata/Warm_rrr-mpia_0008.fits data/Detector/Calibration/
# copy output to other machine, then sync data and create symlinks (on both)
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_lir_0008.fits output/41_cyc6_noisedata/Hot_lir_0008.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_lir_0008.fits output/41_cyc6_noisedata/Noise_lir_0008.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_lir_0008.fits output/41_cyc6_noisedata/Superhot_lir_0008.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_lir_0008.fits output/41_cyc6_noisedata/Warm_lir_0008.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0008.fits output/41_cyc6_noisedata/Hot_rrr-mpia_0008.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_rrr-mpia_0008.fits output/41_cyc6_noisedata/Noise_rrr-mpia_0008.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_rrr-mpia_0008.fits output/41_cyc6_noisedata/Superhot_rrr-mpia_0008.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_rrr-mpia_0008.fits output/41_cyc6_noisedata/Warm_rrr-mpia_0008.fits

# 10/10/14
##########
# cyc6: non-linearity data
run p_42_cyc6_nonlinearity_data.py lir 0
run p_42_cyc6_nonlinearity_data.py rrr-mpia 0

# 27/10/14
##########
# steo by step
run p_42_cyc6_nonlinearity_data.py rrr-mpia 2
run p_42_cyc6_nonlinearity_data.py rrr-mpia 3

# 31/10/14
##########
run p_42_cyc6_nonlinearity_data.py rrr-mpia 4
run p_42_cyc6_nonlinearity_data.py rrr-mpia 5
run p_42_cyc6_nonlinearity_data.py rrr-mpia 6

# median clip cycle 7
# 1st noise data
run p_43_cyc7_medianclip.py 1
# 2nd noise data
run p_43_cyc7_medianclip.py 2

# 01/11/14
##########
# Test stitching of full frame from windows
run p_44_wintest.py 1
run p_44_wintest.py 2

# 02/11/14
##########
# Create ouptut folder in 43_cyc7_medianclip and move 1st noise data there
# cycle 7: Readnoise processing 1st run
run p_45_cyc7_noisedata1.py lir 1
run p_45_cyc7_noisedata1.py lir 2
run p_45_cyc7_noisedata1.py lir 3
run p_45_cyc7_noisedata1.py rrr-mpia 1
run p_45_cyc7_noisedata1.py rrr-mpia 2
run p_45_cyc7_noisedata1.py rrr-mpia 3

# cycle 7: Readnoise processing 2nd run
run p_46_cyc7_noisedata2.py lir 1
run p_46_cyc7_noisedata2.py lir 2
run p_46_cyc7_noisedata2.py lir 3
run p_46_cyc7_noisedata2.py rrr-mpia 1
run p_46_cyc7_noisedata2.py rrr-mpia 2
run p_46_cyc7_noisedata2.py rrr-mpia 3

# Move output data to repository
mv output/45_cyc7_noisedata1/Hot_lir_0009.fits data/Detector/Calibration/
mv output/45_cyc7_noisedata1/Noise_lir_0009.fits data/Detector/Calibration/
mv output/45_cyc7_noisedata1/Superhot_lir_0009.fits data/Detector/Calibration/
mv output/45_cyc7_noisedata1/Warm_lir_0009.fits data/Detector/Calibration/
mv output/45_cyc7_noisedata1/Hot_rrr-mpia_0009.fits data/Detector/Calibration/
mv output/45_cyc7_noisedata1/Noise_rrr-mpia_0009.fits data/Detector/Calibration/
mv output/45_cyc7_noisedata1/Superhot_rrr-mpia_0009.fits data/Detector/Calibration/
mv output/45_cyc7_noisedata1/Warm_rrr-mpia_0009.fits data/Detector/Calibration/
# copy output to other machine, then sync data and create symlinks (on both)
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_lir_0009.fits output/45_cyc7_noisedata1/Hot_lir_0009.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_lir_0009.fits output/45_cyc7_noisedata1/Noise_lir_0009.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_lir_0009.fits output/45_cyc7_noisedata1/Superhot_lir_0009.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_lir_0009.fits output/45_cyc7_noisedata1/Warm_lir_0009.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0009.fits output/45_cyc7_noisedata1/Hot_rrr-mpia_0009.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_rrr-mpia_0009.fits output/45_cyc7_noisedata1/Noise_rrr-mpia_0009.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_rrr-mpia_0009.fits output/45_cyc7_noisedata1/Superhot_rrr-mpia_0009.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_rrr-mpia_0009.fits output/45_cyc7_noisedata1/Warm_rrr-mpia_0009.fits


# Move output data to repository
mv output/46_cyc7_noisedata2/Hot_lir_0010.fits data/Detector/Calibration/
mv output/46_cyc7_noisedata2/Noise_lir_0010.fits data/Detector/Calibration/
mv output/46_cyc7_noisedata2/Superhot_lir_0010.fits data/Detector/Calibration/
mv output/46_cyc7_noisedata2/Warm_lir_0010.fits data/Detector/Calibration/
mv output/46_cyc7_noisedata2/Hot_rrr-mpia_0010.fits data/Detector/Calibration/
mv output/46_cyc7_noisedata2/Noise_rrr-mpia_0010.fits data/Detector/Calibration/
mv output/46_cyc7_noisedata2/Superhot_rrr-mpia_0010.fits data/Detector/Calibration/
mv output/46_cyc7_noisedata2/Warm_rrr-mpia_0010.fits data/Detector/Calibration/
# copy output to other machine, then sync data and create symlinks (on both)
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_lir_0010.fits output/46_cyc7_noisedata2/Hot_lir_0010.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_lir_0010.fits output/46_cyc7_noisedata2/Noise_lir_0010.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_lir_0010.fits output/46_cyc7_noisedata2/Superhot_lir_0010.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_lir_0010.fits output/46_cyc7_noisedata2/Warm_lir_0010.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0010.fits output/46_cyc7_noisedata2/Hot_rrr-mpia_0010.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Noise_rrr-mpia_0010.fits output/46_cyc7_noisedata2/Noise_rrr-mpia_0010.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Superhot_rrr-mpia_0010.fits output/46_cyc7_noisedata2/Superhot_rrr-mpia_0010.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Warm_rrr-mpia_0010.fits output/46_cyc7_noisedata2/Warm_rrr-mpia_0010.fits

# 03/11/2014
############
# Flatfield data and nonlinearity
# on panic22
run p_47_cyc7_nonlinearity_data.py lir 1
run p_47_cyc7_nonlinearity_data.py rrr-mpia 1
# sync median clipped files
# plot ramps
run p_47_cyc7_nonlinearity_data.py lir 2
run p_47_cyc7_nonlinearity_data.py rrr-mpia 2

# 07/11/2014
############
# plot ramps again
run p_47_cyc7_nonlinearity_data.py lir 2
run p_47_cyc7_nonlinearity_data.py rrr-mpia 2

# 14/11/2014
############
# Fit low signal e function
run p_47_cyc7_nonlinearity_data.py lir 3
run p_47_cyc7_nonlinearity_data.py rrr-mpia 3

# 17/11/2014
############
# Plot linear slope data
run p_47_cyc7_nonlinearity_data.py lir 4
run p_47_cyc7_nonlinearity_data.py rrr-mpia 4

# redo median clip cycle 7 w/o first exposure
# 1st noise data
run p_43_cyc7_medianclip.py 1
# 2nd noise data
run p_43_cyc7_medianclip.py 2

# 18/11/2014
############
# Fit polynomials
run p_47_cyc7_nonlinearity_data.py lir 5
run p_47_cyc7_nonlinearity_data.py rrr-mpia 5

# cycle 7: Redo readnoise processing 1st run w/o 1st exposure
run p_45_cyc7_noisedata1.py lir 1
run p_45_cyc7_noisedata1.py lir 2
run p_45_cyc7_noisedata1.py lir 3
run p_45_cyc7_noisedata1.py rrr-mpia 1
run p_45_cyc7_noisedata1.py rrr-mpia 2
run p_45_cyc7_noisedata1.py rrr-mpia 3

# Move output data to repository
mv output/45_cyc7_noisedata1/Hot_lir_0009.fits data/Detector/Calibration/
mv output/45_cyc7_noisedata1/Noise_lir_0009.fits data/Detector/Calibration/
mv output/45_cyc7_noisedata1/Superhot_lir_0009.fits data/Detector/Calibration/
mv output/45_cyc7_noisedata1/Warm_lir_0009.fits data/Detector/Calibration/
mv output/45_cyc7_noisedata1/Hot_rrr-mpia_0009.fits data/Detector/Calibration/
mv output/45_cyc7_noisedata1/Noise_rrr-mpia_0009.fits data/Detector/Calibration/
mv output/45_cyc7_noisedata1/Superhot_rrr-mpia_0009.fits data/Detector/Calibration/
mv output/45_cyc7_noisedata1/Warm_rrr-mpia_0009.fits data/Detector/Calibration/
# copy output to other machine, then sync data and create symlinks (on both)
ln -fs ~/work/PANIC/data/Detector/Calibration/Hot_lir_0009.fits output/45_cyc7_noisedata1/Hot_lir_0009.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Noise_lir_0009.fits output/45_cyc7_noisedata1/Noise_lir_0009.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Superhot_lir_0009.fits output/45_cyc7_noisedata1/Superhot_lir_0009.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Warm_lir_0009.fits output/45_cyc7_noisedata1/Warm_lir_0009.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0009.fits output/45_cyc7_noisedata1/Hot_rrr-mpia_0009.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Noise_rrr-mpia_0009.fits output/45_cyc7_noisedata1/Noise_rrr-mpia_0009.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Superhot_rrr-mpia_0009.fits output/45_cyc7_noisedata1/Superhot_rrr-mpia_0009.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Warm_rrr-mpia_0009.fits output/45_cyc7_noisedata1/Warm_rrr-mpia_0009.fits

# cycle 7: Redo readnoise processing 2nd run w/o 1st exposure
run p_46_cyc7_noisedata2.py lir 1
run p_46_cyc7_noisedata2.py lir 2
run p_46_cyc7_noisedata2.py lir 3
run p_46_cyc7_noisedata2.py rrr-mpia 1
run p_46_cyc7_noisedata2.py rrr-mpia 2
run p_46_cyc7_noisedata2.py rrr-mpia 3

# Move output data to repository
mv output/46_cyc7_noisedata2/Hot_lir_0010.fits data/Detector/Calibration/
mv output/46_cyc7_noisedata2/Noise_lir_0010.fits data/Detector/Calibration/
mv output/46_cyc7_noisedata2/Superhot_lir_0010.fits data/Detector/Calibration/
mv output/46_cyc7_noisedata2/Warm_lir_0010.fits data/Detector/Calibration/
mv output/46_cyc7_noisedata2/Hot_rrr-mpia_0010.fits data/Detector/Calibration/
mv output/46_cyc7_noisedata2/Noise_rrr-mpia_0010.fits data/Detector/Calibration/
mv output/46_cyc7_noisedata2/Superhot_rrr-mpia_0010.fits data/Detector/Calibration/
mv output/46_cyc7_noisedata2/Warm_rrr-mpia_0010.fits data/Detector/Calibration/
# copy output to other machine, then sync data and create symlinks (on both)
ln -fs ~/work/PANIC/data/Detector/Calibration/Hot_lir_0010.fits output/46_cyc7_noisedata2/Hot_lir_0010.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Noise_lir_0010.fits output/46_cyc7_noisedata2/Noise_lir_0010.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Superhot_lir_0010.fits output/46_cyc7_noisedata2/Superhot_lir_0010.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Warm_lir_0010.fits output/46_cyc7_noisedata2/Warm_lir_0010.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0010.fits output/46_cyc7_noisedata2/Hot_rrr-mpia_0010.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Noise_rrr-mpia_0010.fits output/46_cyc7_noisedata2/Noise_rrr-mpia_0010.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Superhot_rrr-mpia_0010.fits output/46_cyc7_noisedata2/Superhot_rrr-mpia_0010.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Warm_rrr-mpia_0010.fits output/46_cyc7_noisedata2/Warm_rrr-mpia_0010.fits

# Plot nonlinearity info
run p_47_cyc7_nonlinearity_data.py lir 6
run p_47_cyc7_nonlinearity_data.py rrr-mpia 6

# Create MEF output, plots, GEIRS bad pixel file
run p_47_cyc7_nonlinearity_data.py lir 7
run p_47_cyc7_nonlinearity_data.py rrr-mpia 7
run p_47_cyc7_nonlinearity_data.py lir 8
run p_47_cyc7_nonlinearity_data.py rrr-mpia 8
run p_47_cyc7_nonlinearity_data.py lir 9
run p_47_cyc7_nonlinearity_data.py rrr-mpia 9

# copy output to other machine, then sync data and create symlinks (on both)
mv output/47_cyc7_nonlinearity_data_lir/NONLIN_LIR_0002.fits data/Detector/Calibration/
mv output/47_cyc7_nonlinearity_data_lir/mNONLIN_LIR_01.00.fits data/Detector/Calibration/
mv output/47_cyc7_nonlinearity_data_rrr-mpia/NONLIN_RRR-MPIA_0002.fits data/Detector/Calibration/
mv output/47_cyc7_nonlinearity_data_rrr-mpia/mNONLIN_RRR-MPIA_01.00.fits data/Detector/Calibration/

ln -fs ~/work/PANIC/data/Detector/Calibration/NONLIN_LIR_0002.fits output/47_cyc7_nonlinearity_data_lir/NONLIN_LIR_0002.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/mNONLIN_LIR_01.00.fits output/47_cyc7_nonlinearity_data_lir/mNONLIN_LIR_01.00.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/NONLIN_RRR-MPIA_0002.fits output/47_cyc7_nonlinearity_data_rrr-mpia/NONLIN_RRR-MPIA_0002.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/mNONLIN_RRR-MPIA_01.00.fits output/47_cyc7_nonlinearity_data_rrr-mpia/mNONLIN_RRR-MPIA_01.00.fits

# 19/11/2014
############
# Plot linear slope data with full ramps
run p_47_cyc7_nonlinearity_data.py lir 4
run p_47_cyc7_nonlinearity_data.py rrr-mpia 4

# 27/11/2014
############
# Test nonlinearity correction
run p_48_test_nonlinearity.py lir 1 calc
run p_48_test_nonlinearity.py lir 1 plot
run p_48_test_nonlinearity.py lir 1 corr
run p_48_test_nonlinearity.py lir 2 all
run p_48_test_nonlinearity.py lir 3 all
run p_48_test_nonlinearity.py lir 4 all
run p_48_test_nonlinearity.py lir 5 all
run p_48_test_nonlinearity.py rrr-mpia 1 all
run p_48_test_nonlinearity.py rrr-mpia 2 all
run p_48_test_nonlinearity.py rrr-mpia 3 all
run p_48_test_nonlinearity.py rrr-mpia 4 all
run p_48_test_nonlinearity.py rrr-mpia 5 all

# 27/11/2014
############
# Test nonlinearity correction: residual calculation
run p_48_test_nonlinearity.py lir 1 resid
run p_48_test_nonlinearity.py lir 2 resid

# 05/12/2014
############
# Test nonlinearity correction: residual plot
run p_48_test_nonlinearity.py lir 1 plotresid
run p_48_test_nonlinearity.py lir 2 plotresid
run p_48_test_nonlinearity.py rrr-mpia 2 resid

# 05/12/2014
############
run p_48_test_nonlinearity.py rrr-mpia 2 plotresid
run p_48_test_nonlinearity.py rrr-mpia 1 resid

# 07/12/2014
############
# Median average linearity test flats
# on panic22
run p_47_cyc7_nonlinearity_data.py lir 3
run p_47_cyc7_nonlinearity_data.py rrr-mpia 3
# Sync median averaged files

# 09/12/2014
############
# Test nonlinearity correction: residual plot
run p_48_test_nonlinearity.py rrr-mpia 1 plotresid
# Test nonlinearity correction: 10s saturation
run p_48_test_nonlinearity.py lir 6 all
run p_48_test_nonlinearity.py rrr-mpia 6 all
# Replot ramps
run p_48_test_nonlinearity.py lir 1 plot
run p_48_test_nonlinearity.py lir 2 plot
run p_48_test_nonlinearity.py lir 3 plot
run p_48_test_nonlinearity.py lir 4 plot
run p_48_test_nonlinearity.py lir 5 plot
run p_48_test_nonlinearity.py lir 6 plot
run p_48_test_nonlinearity.py rrr-mpia 1 plot
run p_48_test_nonlinearity.py rrr-mpia 2 plot
run p_48_test_nonlinearity.py rrr-mpia 3 plot
run p_48_test_nonlinearity.py rrr-mpia 4 plot
run p_48_test_nonlinearity.py rrr-mpia 5 plot

# 10/12/2014
############
# Replot ramps
run p_48_test_nonlinearity.py lir 1 plot
run p_48_test_nonlinearity.py lir 2 plot
run p_48_test_nonlinearity.py lir 3 plot
run p_48_test_nonlinearity.py lir 4 plot
run p_48_test_nonlinearity.py lir 5 plot
run p_48_test_nonlinearity.py lir 6 plot
run p_48_test_nonlinearity.py rrr-mpia 1 plot
run p_48_test_nonlinearity.py rrr-mpia 2 plot
run p_48_test_nonlinearity.py rrr-mpia 3 plot
run p_48_test_nonlinearity.py rrr-mpia 4 plot
run p_48_test_nonlinearity.py rrr-mpia 5 plot
run p_48_test_nonlinearity.py rrr-mpia 6 plot

# 11/12/2014
############
# Reduce linear correction limit
run p_47_cyc7_nonlinearity_data.py lir 5.1
run p_47_cyc7_nonlinearity_data.py lir 6
run p_47_cyc7_nonlinearity_data.py lir 7
run p_47_cyc7_nonlinearity_data.py lir 8
run p_47_cyc7_nonlinearity_data.py rrr-mpia 5.1
run p_47_cyc7_nonlinearity_data.py rrr-mpia 6
run p_47_cyc7_nonlinearity_data.py rrr-mpia 7
run p_47_cyc7_nonlinearity_data.py rrr-mpia 8

# Move output data to repository
mv output/47_cyc7_nonlinearity_data_lir/NONLIN_LIR_0003.fits data/Detector/Calibration/
mv output/47_cyc7_nonlinearity_data_lir/mNONLIN_LIR_01.01.fits data/Detector/Calibration/
mv output/47_cyc7_nonlinearity_data_rrr-mpia/NONLIN_RRR-MPIA_0003.fits data/Detector/Calibration/
mv output/47_cyc7_nonlinearity_data_rrr-mpia/mNONLIN_RRR-MPIA_01.01.fits data/Detector/Calibration/

# copy output to other machine, then sync data and create symlinks (on both)
ln -fs ~/work/PANIC/data/Detector/Calibration/NONLIN_LIR_0003.fits output/47_cyc7_nonlinearity_data_lir/NONLIN_LIR_0003.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/mNONLIN_LIR_01.01.fits output/47_cyc7_nonlinearity_data_lir/mNONLIN_LIR_01.01.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/NONLIN_RRR-MPIA_0003.fits output/47_cyc7_nonlinearity_data_rrr-mpia/NONLIN_RRR-MPIA_0003.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/mNONLIN_RRR-MPIA_01.01.fits output/47_cyc7_nonlinearity_data_rrr-mpia/mNONLIN_RRR-MPIA_01.01.fits

# Test nonlinearity correction again
run p_48_test_nonlinearity.py lir 6 all
run p_48_test_nonlinearity.py rrr-mpia 6 all
run p_48_test_nonlinearity.py lir 1 all
# complete after crash
run p_48_test_nonlinearity.py lir 1 resid
run p_48_test_nonlinearity.py lir 1 plotresid
run p_48_test_nonlinearity.py rrr-mpia 1 all

# 19/12/2014
############
# Tilt plane fits
run p_49_2.2_tilt.py 1
run p_49_2.2_tilt.py 2
run p_49_2.2_tilt.py 3
run p_49_2.2_tilt.py 4
run p_49_2.2_tilt.py 5
run p_49_2.2_tilt.py 6
run p_49_2.2_tilt.py 7
run p_49_2.2_tilt.py 13

# 04/02/2015
############
# Test nonlinearity correction again
run p_48_test_nonlinearity.py lir 2 all

# 06/02/2015
############
# Test nonlinearity correction again, corrected saturation
run p_48_test_nonlinearity.py lir 5 all
# Test nonlinearity correction again, excluded residuum duplicates
run p_48_test_nonlinearity.py lir 5 resid
run p_48_test_nonlinearity.py lir 5 plotresid
run p_48_test_nonlinearity.py lir 2 resid

# 09/02/2015
############
run p_48_test_nonlinearity.py lir 2 plotresid
run p_48_test_nonlinearity.py lir 1 resid

# 10/02/2015
############
run p_48_test_nonlinearity.py lir 1 plotresid

# cycle 7: Redo readnoise processing 1st run, new gains
run p_45_cyc7_noisedata1.py lir 1
run p_45_cyc7_noisedata1.py lir 2
run p_45_cyc7_noisedata1.py lir 3
run p_45_cyc7_noisedata1.py rrr-mpia 1
run p_45_cyc7_noisedata1.py rrr-mpia 2
run p_45_cyc7_noisedata1.py rrr-mpia 3

# Move output data to repository
mv output/45_cyc7_noisedata1/Hot_lir_0009.fits data/Detector/Calibration/
mv output/45_cyc7_noisedata1/Noise_lir_0009.fits data/Detector/Calibration/
mv output/45_cyc7_noisedata1/Superhot_lir_0009.fits data/Detector/Calibration/
mv output/45_cyc7_noisedata1/Warm_lir_0009.fits data/Detector/Calibration/
mv output/45_cyc7_noisedata1/Hot_rrr-mpia_0009.fits data/Detector/Calibration/
mv output/45_cyc7_noisedata1/Noise_rrr-mpia_0009.fits data/Detector/Calibration/
mv output/45_cyc7_noisedata1/Superhot_rrr-mpia_0009.fits data/Detector/Calibration/
mv output/45_cyc7_noisedata1/Warm_rrr-mpia_0009.fits data/Detector/Calibration/
# copy output to other machine, then sync data and create symlinks (on both)
ln -fs ~/work/PANIC/data/Detector/Calibration/Hot_lir_0009.fits output/45_cyc7_noisedata1/Hot_lir_0009.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Noise_lir_0009.fits output/45_cyc7_noisedata1/Noise_lir_0009.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Superhot_lir_0009.fits output/45_cyc7_noisedata1/Superhot_lir_0009.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Warm_lir_0009.fits output/45_cyc7_noisedata1/Warm_lir_0009.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0009.fits output/45_cyc7_noisedata1/Hot_rrr-mpia_0009.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Noise_rrr-mpia_0009.fits output/45_cyc7_noisedata1/Noise_rrr-mpia_0009.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Superhot_rrr-mpia_0009.fits output/45_cyc7_noisedata1/Superhot_rrr-mpia_0009.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Warm_rrr-mpia_0009.fits output/45_cyc7_noisedata1/Warm_rrr-mpia_0009.fits

# cycle 7: Redo readnoise processing 2nd run, new gains
run p_46_cyc7_noisedata2.py lir 1
run p_46_cyc7_noisedata2.py lir 2
run p_46_cyc7_noisedata2.py lir 3
run p_46_cyc7_noisedata2.py rrr-mpia 1
run p_46_cyc7_noisedata2.py rrr-mpia 2
run p_46_cyc7_noisedata2.py rrr-mpia 3

# Move output data to repository
mv output/46_cyc7_noisedata2/Hot_lir_0010.fits data/Detector/Calibration/
mv output/46_cyc7_noisedata2/Noise_lir_0010.fits data/Detector/Calibration/
mv output/46_cyc7_noisedata2/Superhot_lir_0010.fits data/Detector/Calibration/
mv output/46_cyc7_noisedata2/Warm_lir_0010.fits data/Detector/Calibration/
mv output/46_cyc7_noisedata2/Hot_rrr-mpia_0010.fits data/Detector/Calibration/
mv output/46_cyc7_noisedata2/Noise_rrr-mpia_0010.fits data/Detector/Calibration/
mv output/46_cyc7_noisedata2/Superhot_rrr-mpia_0010.fits data/Detector/Calibration/
mv output/46_cyc7_noisedata2/Warm_rrr-mpia_0010.fits data/Detector/Calibration/
# copy output to other machine, then sync data and create symlinks (on both)
ln -fs ~/work/PANIC/data/Detector/Calibration/Hot_lir_0010.fits output/46_cyc7_noisedata2/Hot_lir_0010.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Noise_lir_0010.fits output/46_cyc7_noisedata2/Noise_lir_0010.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Superhot_lir_0010.fits output/46_cyc7_noisedata2/Superhot_lir_0010.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Warm_lir_0010.fits output/46_cyc7_noisedata2/Warm_lir_0010.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0010.fits output/46_cyc7_noisedata2/Hot_rrr-mpia_0010.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Noise_rrr-mpia_0010.fits output/46_cyc7_noisedata2/Noise_rrr-mpia_0010.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Superhot_rrr-mpia_0010.fits output/46_cyc7_noisedata2/Superhot_rrr-mpia_0010.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Warm_rrr-mpia_0010.fits output/46_cyc7_noisedata2/Warm_rrr-mpia_0010.fits

# Test nonlinearity correction again
run p_48_test_nonlinearity.py lir 6 resid
run p_48_test_nonlinearity.py lir 6 plotresid
run p_48_test_nonlinearity.py lir 4 all
run p_48_test_nonlinearity.py lir 3 all

# 11/02/2015
############
# Saturation level, flatfield stats, cold pix map
run p_51_cyc7_saturation.py 1 lir
run p_51_cyc7_saturation.py 2 lir
run p_51_cyc7_saturation.py 4 lir
run p_51_cyc7_saturation.py 1 rrr-mpia
run p_51_cyc7_saturation.py 2 rrr-mpia
run p_51_cyc7_saturation.py 4 rrr-mpia

# Move output data to repository
mv output/51_cyc7_saturation/Cold_lir_0003.fits data/Detector/Calibration/
mv output/51_cyc7_saturation/Cold_rrr-mpia_0003.fits data/Detector/Calibration/
# copy output to other machine, then sync data and create symlinks (on both)
ln -s ~/work/PANIC/data/Detector/Calibration/Cold_lir_0003.fits output/51_cyc7_saturation/Cold_lir_0003.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Cold_rrr-mpia_0003.fits output/51_cyc7_saturation/Cold_rrr-mpia_0003.fits

# Saturation level files
run p_51_cyc7_saturation.py 3 lir
run p_51_cyc7_saturation.py 3 rrr-mpia

# Move output data to repository
mv output/51_cyc7_saturation/Satlevel_rrr-mpia_CDS_0003.fits data/Detector/Calibration/
mv output/51_cyc7_saturation/Satlevel_lir_CDS_0003.fits data/Detector/Calibration/
# copy output to other machine, then sync data and create symlinks (on both)
ln -s ~/work/PANIC/data/Detector/Calibration/Satlevel_rrr-mpia_CDS_0003.fits output/51_cyc7_saturation/Satlevel_rrr-mpia_CDS_0003.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Satlevel_lir_CDS_0003.fits output/51_cyc7_saturation/Satlevel_lir_CDS_0003.fits

# Dark cube analysis
run p_52_cyc7_darkcube.py rrr-mpia 1
run p_52_cyc7_darkcube.py lir 1

# 12/02/2015
############
# Dark cube analysis ctd
run p_52_cyc7_darkcube.py rrr-mpia 2
run p_52_cyc7_darkcube.py rrr-mpia 3
run p_52_cyc7_darkcube.py rrr-mpia 4
run p_52_cyc7_darkcube.py lir 2
run p_52_cyc7_darkcube.py lir 3
run p_52_cyc7_darkcube.py lir 4

# Move output data to repository
mv output/52_cyc7_darkcube/Dark_rrr-mpia_0004.fits data/Detector/Calibration/
mv output/52_cyc7_darkcube/Darkpoly_rrr-mpia_0004.fits data/Detector/Calibration/
mv output/52_cyc7_darkcube/Dark_lir_0004.fits data/Detector/Calibration/
mv output/52_cyc7_darkcube/Darkpoly_lir_0004.fits data/Detector/Calibration/
# copy output to other machine, then sync data and create symlinks (on both)
ln -s ~/work/PANIC/data/Detector/Calibration/Dark_rrr-mpia_0004.fits output/52_cyc7_darkcube/Dark_rrr-mpia_0004.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Darkpoly_rrr-mpia_0004.fits output/52_cyc7_darkcube/Darkpoly_rrr-mpia_0004.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Dark_lir_0004.fits output/52_cyc7_darkcube/Dark_lir.fits
ln -s ~/work/PANIC/data/Detector/Calibration/Darkpoly_lir_0004.fits output/52_cyc7_darkcube/Darkpoly_lir_0004.fits

# Test nonlinearity correction again
run p_48_test_nonlinearity.py rrr-mpia 6 all
run p_48_test_nonlinearity.py rrr-mpia 1 resid

# 15/02/2015
############
run p_48_test_nonlinearity.py rrr-mpia 1 plotresid

# 16/02/2015
############
run p_48_test_nonlinearity.py rrr-mpia 2 all
run p_48_test_nonlinearity.py rrr-mpia 4 all

# 17/02/2015
############
run p_48_test_nonlinearity.py rrr-mpia 5 all
run p_48_test_nonlinearity.py rrr-mpia 3 all

# 21/04/2015
############
# median clip cycle 7 panic35 noise data
run p_43_cyc7_medianclip.py 4

# cycle 7: readnoise panic35
run p_53_cyc7_noisedata35.py lir 1
run p_53_cyc7_noisedata35.py lir 2
run p_53_cyc7_noisedata35.py lir 3
run p_53_cyc7_noisedata35.py rrr-mpia 1
run p_53_cyc7_noisedata35.py rrr-mpia 2
run p_53_cyc7_noisedata35.py rrr-mpia 3

# Move output data to repository
mv output/53_cyc7_noisedata35/Hot_lir_0009a.fits data/Detector/Calibration/
mv output/53_cyc7_noisedata35/Noise_lir_0009a.fits data/Detector/Calibration/
mv output/53_cyc7_noisedata35/Superhot_lir_0009a.fits data/Detector/Calibration/
mv output/53_cyc7_noisedata35/Warm_lir_0009a.fits data/Detector/Calibration/
mv output/53_cyc7_noisedata35/Hot_rrr-mpia_0009a.fits data/Detector/Calibration/
mv output/53_cyc7_noisedata35/Noise_rrr-mpia_0009a.fits data/Detector/Calibration/
mv output/53_cyc7_noisedata35/Superhot_rrr-mpia_0009a.fits data/Detector/Calibration/
mv output/53_cyc7_noisedata35/Warm_rrr-mpia_0009a.fits data/Detector/Calibration/
# copy output to other machine, then sync data and create symlinks (on both)
ln -fs ~/work/PANIC/data/Detector/Calibration/Hot_lir_0009a.fits output/53_cyc7_noisedata35/Hot_lir_0009a.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Noise_lir_0009a.fits output/53_cyc7_noisedata35/Noise_lir_0009a.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Superhot_lir_0009a.fits output/53_cyc7_noisedata35/Superhot_lir_0009a.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Warm_lir_0009a.fits output/53_cyc7_noisedata35/Warm_lir_0009a.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0009a.fits output/53_cyc7_noisedata35/Hot_rrr-mpia_0009a.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Noise_rrr-mpia_0009a.fits output/53_cyc7_noisedata35/Noise_rrr-mpia_0009a.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Superhot_rrr-mpia_0009a.fits output/53_cyc7_noisedata35/Superhot_rrr-mpia_0009a.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Warm_rrr-mpia_0009a.fits output/53_cyc7_noisedata35/Warm_rrr-mpia_0009a.fits

# 23/04/2015
############
# cycle 8: readnoise at end
run p_54_cyc8_noisedata.py lir 0
run p_54_cyc8_noisedata.py lir 1
run p_54_cyc8_noisedata.py lir 2
run p_54_cyc8_noisedata.py lir 3
run p_54_cyc8_noisedata.py rrr-mpia 0
run p_54_cyc8_noisedata.py rrr-mpia 1
run p_54_cyc8_noisedata.py rrr-mpia 2
run p_54_cyc8_noisedata.py rrr-mpia 3

# Move output data to repository
mv output/54_cyc8_noisedata/Hot_lir_0011.fits data/Detector/Calibration/
mv output/54_cyc8_noisedata/Noise_lir_0011.fits data/Detector/Calibration/
mv output/54_cyc8_noisedata/Superhot_lir_0011.fits data/Detector/Calibration/
mv output/54_cyc8_noisedata/Warm_lir_0011.fits data/Detector/Calibration/
mv output/54_cyc8_noisedata/Hot_rrr-mpia_0011.fits data/Detector/Calibration/
mv output/54_cyc8_noisedata/Noise_rrr-mpia_0011.fits data/Detector/Calibration/
mv output/54_cyc8_noisedata/Superhot_rrr-mpia_0011.fits data/Detector/Calibration/
mv output/54_cyc8_noisedata/Warm_rrr-mpia_0011.fits data/Detector/Calibration/
# copy output to other machine, then sync data and create symlinks (on both)
ln -fs ~/work/PANIC/data/Detector/Calibration/Hot_lir_0011.fits output/54_cyc8_noisedata/Hot_lir_0011.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Noise_lir_0011.fits output/54_cyc8_noisedata/Noise_lir_0011.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Superhot_lir_0011.fits output/54_cyc8_noisedata/Superhot_lir_0011.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Warm_lir_0011.fits output/54_cyc8_noisedata/Warm_lir_0011.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0011.fits output/54_cyc8_noisedata/Hot_rrr-mpia_0011.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Noise_rrr-mpia_0011.fits output/54_cyc8_noisedata/Noise_rrr-mpia_0011.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Superhot_rrr-mpia_0011.fits output/54_cyc8_noisedata/Superhot_rrr-mpia_0011.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Warm_rrr-mpia_0011.fits output/54_cyc8_noisedata/Warm_rrr-mpia_0011.fits

# 11/05/2015
############
# cycle 9: readnoise at end
run p_55_cyc9_noisedata1.py lir 0
run p_55_cyc9_noisedata1.py lir 1
run p_55_cyc9_noisedata1.py lir 2
run p_55_cyc9_noisedata1.py lir 3
run p_55_cyc9_noisedata1.py rrr-mpia 0
run p_55_cyc9_noisedata1.py rrr-mpia 1
run p_55_cyc9_noisedata1.py rrr-mpia 2
run p_55_cyc9_noisedata1.py rrr-mpia 3

# Move output data to repository
mv output/55_cyc9_noisedata1/Hot_lir_0012.fits data/Detector/Calibration/
mv output/55_cyc9_noisedata1/Noise_lir_0012.fits data/Detector/Calibration/
mv output/55_cyc9_noisedata1/Superhot_lir_0012.fits data/Detector/Calibration/
mv output/55_cyc9_noisedata1/Warm_lir_0012.fits data/Detector/Calibration/
mv output/55_cyc9_noisedata1/Hot_rrr-mpia_0012.fits data/Detector/Calibration/
mv output/55_cyc9_noisedata1/Noise_rrr-mpia_0012.fits data/Detector/Calibration/
mv output/55_cyc9_noisedata1/Superhot_rrr-mpia_0012.fits data/Detector/Calibration/
mv output/55_cyc9_noisedata1/Warm_rrr-mpia_0012.fits data/Detector/Calibration/
# copy output to other machine, then sync data and create symlinks (on both)
ln -fs ~/work/PANIC/data/Detector/Calibration/Hot_lir_0012.fits output/55_cyc9_noisedata1/Hot_lir_0012.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Noise_lir_0012.fits output/55_cyc9_noisedata1/Noise_lir_0012.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Superhot_lir_0012.fits output/55_cyc9_noisedata1/Superhot_lir_0012.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Warm_lir_0012.fits output/55_cyc9_noisedata1/Warm_lir_0012.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Hot_rrr-mpia_0012.fits output/55_cyc9_noisedata1/Hot_rrr-mpia_0012.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Noise_rrr-mpia_0012.fits output/55_cyc9_noisedata1/Noise_rrr-mpia_0012.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Superhot_rrr-mpia_0012.fits output/55_cyc9_noisedata1/Superhot_rrr-mpia_0012.fits
ln -fs ~/work/PANIC/data/Detector/Calibration/Warm_rrr-mpia_0012.fits output/55_cyc9_noisedata1/Warm_rrr-mpia_0012.fits

# Flatfield data for nonlinearity test
# on panic35
run p_56_cyc9_test_nonlinearity.py lir 1 medavg
# median average in QL
# sync median clipped files
run p_56_cyc9_test_nonlinearity.py lir 1 all

# 12/05/2015
############
# Flatfield data for nonlinearity test
# on panic35
run p_56_cyc9_test_nonlinearity.py rrr-mpia 1 medavg
# median average in QL
# sync median clipped files
run p_56_cyc9_test_nonlinearity.py rrr-mpia 1 all

# 16/07/2015
############
# Comparison of bad pixel masks
run p_57_badpix_comparison.py lir 1
run p_57_badpix_comparison.py lir 2
run p_57_badpix_comparison.py rrr-mpia 1
run p_57_badpix_comparison.py rrr-mpia 2

# 19/11/2015
############
# Create detector hot pixel evolution plots
run p_58_hotpix_evolution.py 1
run p_58_hotpix_evolution.py 2