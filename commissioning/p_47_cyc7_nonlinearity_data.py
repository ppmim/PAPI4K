#!/usr/bin/env python
#########################################################################
# PANIC data
#########################################################################
# Create nonlinearity correction data from calibration at CAHA
# Inputs:
# - original data form DET_FLAT_3_3
# - manual median averaging with PANIC QL (faster) after 1st step
#
# usage: p_47_cyc7_nonlinearity_data.py [-h] [--nolog]
#                                       {rrr-mpia,lir} {1,2,3,4,5,6,7,8,9,0}
# 
# positional arguments:
#   {rrr-mpia,lir}        Readout mode string
#   {1,2,3,4,5,6,7,8,9,0}
#                         Step to execute: (1)Create CDS data (2)Plot ramps and
#                         median (3)Fit linear slope (4)Plot linear slope data
#                         (5)Fit polynomial (6)Plot fit info (7)Write as MEF
#                         (8)Create image of correction limit (9)Create GEIRS
#                         bad pixel map file (0)All steps 3-9 in a row
# 
# optional arguments:
#   -h, --help            show this help message and exit
#   --nolog               Do not write output log file
#
# 1.0 14/11/2014 BD Creation from p_42_cyc6_nonlinearity_data 1.0.1
#	1) Added CDS generation and ramp plots
#	2) Added nonlinear residual plots
#	3) Added correction fit plots
#	4) Forced master file output idlemode to wait
# 1.1 18/11/2014 BD Update
#	1) Added creation of GEIRS bad pixel file
#	2) Exclude first two points in polynomial residual cutoff for lir
#	3) Increased relative residual cutoff for max polyfit points
# 1.2 18/11/2014 BD Update
#	1) Fixed CDS file selection
#	2) Added output of true maximum correctable counts
# 1.2.1 18/11/2014 BD Update
#	1) Fixed header of MEF output
#	2) Added rmode to GEIRS bad pixel filename
# 1.3 19/11/2014 BD Update
#	1) Added plot of full ramp with linear slope
# 1.4 11/12/2014 BD Update
#	1) Added reduction of correction limit to 96% saturation
#	2) Adjusted FITS output and header values
#
_name = 'p_47_cyc7_nonlinearity_data.py'
_version = '1.4'
#########################################################################
import numpy as np
from astropy.io import fits
import os
import fnmatch
import argparse
import cPickle as pickle
import matplotlib.pyplot as plt
import datetime
from scipy import optimize

# parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('rmode', type=str, choices=['rrr-mpia', 'lir'], help='Readout mode string')
arghelp = 'Step to execute: (1)Create CDS data (2)Plot ramps and median (3)Fit linear slope (4)Plot linear slope data (5)Fit polynomial (5.1)Adjust maxlimit (6)Plot fit info (7)Write as MEF (8)Create image of correction limit (9)Create GEIRS bad pixel file (0)All steps 3-9 in a row'
parser.add_argument('istep', type=float, choices=[1,2,3,4,5,5.1,6,7,8,9,0], help=arghelp)
parser.add_argument('--nolog', help='Do not write output log file', action='store_true')
args = parser.parse_args()
rmode = args.rmode
istep = args.istep
writelog = not args.nolog

# path to data
# panic22
archivepath = '/data1/PANIC/'
inputpath = '/data2/out/2014-11-01_flat_3_3'
# microwave
inputpath = '/Users/dorner/work/PANIC/Exposures/processed/2014-11-01_flat_3_3'
# aida43216
inputpath = '/home/dorner/work/PANIC/processed/2014-11-01_flat_3_3'

outputpath = 'output/47_cyc7_nonlinearity_data_%s' %rmode
# polynomial order to fit
porder = 4
# parameters of the files, use all images
if rmode == 'rrr-mpia':
	nIDrange = range(1, 32) + range(63, 67)
elif rmode == 'lir':
	nIDrange = range(32, 63) + range(67, 71)
folders = ['2014-11-01_flat_3_3'] * 31 + ['2014-11-02_flat_3_3_pt2'] * 4
filebase = 'DET_FLAT_'
nIDs = len(nIDrange)

if not os.access(outputpath,os.F_OK):
	os.mkdir(outputpath)
if not os.access(inputpath,os.F_OK):
	os.mkdir(inputpath)

def savepickle(filename, data):
	'''Save data in pickle file: filename, data'''
	pkl = open(filename, 'wb')
	pickle.dump(data, pkl)
	pkl.close()

def loadpickle(filename):
	'''Load data from pickle file: filename'''
	pkl = open(filename, 'rb')
	data = pickle.load(pkl)
	pkl.close()
	return data

def nowtime():
	return datetime.datetime.now().isoformat()

def pr(msg):
	'''Print messages and write to log file'''
	print msg
	if writelog:
		logfile = open(os.path.join(outputpath, 'Logfile.txt'), 'a')
		logfile.write(msg + '\n')
		logfile.close()

def polyval_map_offset(poly, map):
	'''Evaluate individual polynomials on array.
	
	Input
	-----
	poly : array_like
		   Polynomial coefficients with constant offset. The order
		   must be along the last axis.
	map : array_like
		  Data array.
		  
	Returns
	-------
	polymap : array_like
			  Result of evaluation, same shape as map
	'''
	order = poly.shape[-1]
	polymap = map * 0
	for io in range(order):
		polymap += map**(io) * poly[Ellipsis, -io-1]
	return polymap

def polyval_map(poly, map):
	'''Evaluate individual polynomials on array.
	
	Input
	-----
	poly : array_like
		   Polynomial coefficients without constant offset. The order
		   must be along the last axis.
	map : array_like
		  Data array.
		  
	Returns
	-------
	polymap : array_like
			  Result of evaluation, same shape as map
	'''
	order = poly.shape[-1]
	polymap = map * 0
	for io in range(order):
		polymap += map**(io+1) * poly[Ellipsis, -io-1]
	return polymap

pr('########################')
pr('# New script execution #')
pr('########################')
pr('# %s, %s' %(_name, _version))
pr('# ' + nowtime())
pr('# Readmode: %s' %rmode)

# Create CDS image files
if istep in [1]:
	pr('# Creating CDS image files')
	filebase = 'DET_FLAT_'
	nIDs = len(nIDrange)
	istartlist = [1] * 35
	nexps = 10
	for iID in range(nIDs):
		nID = nIDrange[iID]
		pr('  * nID %i' %nID)
		istart = istartlist[iID]
		folder = folders[iID]
		for iexp in range(nexps):
			# CDS from single frame cubes
			cdsdata = np.zeros((4096, 4096)).astype('int32')
			file = filebase+'%02i_SINGLE_CUBE_%04i.fits' %(nID, iexp+istart)
			hdulist = fits.open(os.path.join(archivepath, folder, file))
			header = hdulist[0].header
			data = np.rollaxis(hdulist[0].data.astype('int32'), 0, 3)
			cdsdata = data[:, :, 1] - data[:, :, 0]
			# create and save fits file
			cdshdu = fits.PrimaryHDU(cdsdata)
			cdshdu.header = header.copy()
			cdshdu.header['HISTORY'] = 'CDS from single frames'
			filename = filebase+'%02i_CDS_%04i.fits' %(nID, iexp+istart)
			pr('    - Saving output file %s' %filename)
			cdshdulist = fits.HDUList([cdshdu])
			cdshdulist.writeto(os.path.join(inputpath, filename), clobber=True)	
	
	pr('IMPORTANT: Please median average files now in QL, do not use first one.')
	pr('Filenames: DET_FLAT_XX_CDS_medclip_0002-0010.fits')
	
# Plot some ramps and median data
if istep in [2]:
	pr('# Plotting some pixel ramps')
	# 4 random pixels per SG
	npx = 4
	np.random.seed(10)
	# as defined below, 1st is j, 2nd is i (nice selection)
	pxys = np.random.randint(4, 2044, (npx,2))
	SGcorners = [[0, 2048], [2048, 2048], [2048, 0], [0, 0]]
	filebase = 'DET_FLAT_'
	nIDs = len(nIDrange)
	istartlist = [1] * 35
	nexps = 10
	for iSG in range(4):
		for ipx in range(npx):
			px = SGcorners[iSG][1] + pxys[ipx, 1]
			py = SGcorners[iSG][0] + pxys[ipx, 0]
			pr('  * pixel %i, %i' %(px+1, py+1))
			# get data vectors
			cdsdata = np.zeros((nIDs, nexps))
			meddata = np.zeros(nIDs)
			itimes = np.zeros(nIDs)
			for iID in range(nIDs):
				nID = nIDrange[iID]
				istart = istartlist[iID]
				for iexp in range(nexps):
					file = filebase+'%02i_CDS_%04i.fits' %(nID, iexp+istart)
					hdulist = fits.open(os.path.join(inputpath, file))
					data = hdulist[0].data.astype('int32')
					cdsdata[iID, iexp] = data[py, px]
				file = filebase+'%02i_CDS_medclip0002-0010.fits' %(nID)
				hdulist = fits.open(os.path.join(inputpath, file))
				data = hdulist[0].data.astype('int32')
				meddata[iID] = data[py, px]
				itimes[iID] = hdulist[0].header['ITIME']
			# Plot data
			plt.figure()
			# plot first image separately
			plt.plot(itimes, cdsdata[:, 0], '+', label='%i'%(1))
			for iexp in range(1, nexps):
				plt.plot(itimes, cdsdata[:, iexp], 'x', label='%i'%(iexp+1))
			plt.plot(itimes, meddata, 'D-', label='Med 2-10', mfc='None', mec='c', ms=8)
			plt.xlim(xmax=itimes[-1]*1.3)
			plt.legend(loc='lower right', ncol=2)
			plt.grid()
			plt.title('Single pixel data ramp %s SG%i' %(rmode, iSG+1))
			plt.xlabel('Integration time / s')
			plt.ylabel('Signal / ADU')
			plt.figtext(0.02, 0.01, 'Pixel %i, %i' %(px+1, py+1), ha='left', style='italic', size=8)
			plt.figtext(0.98, 0.01, 'Data: DET_FLAT_3_3_asrun20141101', ha='right', style='italic', size=8)
			filename = 'Ramp_%s_SG%i_%04i_%04i' %(rmode, iSG+1, px+1, py+1)
			plt.savefig(os.path.join(outputpath, filename + '.png'))
			plt.close()
	
# Fit linear signal
if istep in [0,3]:
	pr('# Creating linear extrapolation')
	levels = np.zeros(nIDs)
	itimes = np.zeros(nIDs)
	#datalist = []
	datacube = np.zeros((4096, 4096, nIDs))
	# load data
	pr('# Loading data')
	for iID in range(nIDs):
		nID = nIDrange[iID]
		pr('  * Loading image number %i' %nID)
		pathlist = os.listdir(inputpath)
		fitsfiles = fnmatch.filter(pathlist, filebase+'%02i_CDS_medclip0002-0010.fits' %(nID))
		if len(fitsfiles) != 1:
			raise IOError('More than one file found for image number %i' %iID)
		# load data, get median
		hdulist = fits.open(os.path.join(inputpath, fitsfiles[0]))
		data = hdulist[0].data
#		datalist.append(data)
		datacube[:, :, iID] = data
		itimes[iID] = hdulist[0].header['ITIME']
		date_obs = hdulist[0].header['DATE-OBS']
	a = np.zeros((4096, 4096))
	alpha = np.zeros((4096, 4096))
	beta = np.zeros((4096, 4096))
	pr('# Fitting exponential function per pixel')
	# exponential function
	def efunc(x, a, alpha, beta):
		return a + alpha * (1 - np.exp(-1.0 * x / beta))
	# loop over pixels
	pingsteps = (np.arange(1,8) * 512) - 1
	# plot 4 random pixels per SG
	npx = 4
	np.random.seed(10)
	# as defined below, 1st is j, 2nd is i (nice selection)
	pxys = np.random.randint(4, 2044, (npx,2))
	SGcorners = [[0, 2048], [2048, 2048], [2048, 0], [0, 0]]
	# expand to all SGs and as list for comparison
	pixlist = []
	for iSG in range(4):
		for ipx in range(npx):
			px = SGcorners[iSG][1] + pxys[ipx, 1]
			py = SGcorners[iSG][0] + pxys[ipx, 0]
			# list has correct order
			pixlist.append([px, py])
	for ipx in range(4096):
		if ipx in pingsteps:
			print '  * ipx %i' %(ipx+1)
		for jpx in range(4096):
			# create data vector
			levels = datacube[ipx, jpx, :]
			# Check if all signal < 10000: no correction
			if levels.max() < 10000:
				# set linear extrapolation to nan
				a[ipx, jpx] = np.nan
				alpha[ipx, jpx] = np.nan
				beta[ipx, jpx] = np.nan
			else:
				# Fit linear slope and save
				# saturation: last data point
				satmax = levels[-1]
				# lin fit max: 20% saturation or 10 points (6s or 7.5s)
				linmax = 0.20 * satmax
				linrange = levels < linmax
				# Check if there are at least 3 points
				if linrange.sum() < 3:
					# set linear extrapolation to nan: no correction
					a[ipx, jpx] = np.nan
					alpha[ipx, jpx] = np.nan
					beta[ipx, jpx] = np.nan
				else:
					if linrange.sum() > 10:
						linrange[10:] = False
					popt, pcov = optimize.curve_fit(efunc, itimes[linrange], levels[linrange], p0=[0, 4e5, 2e2])
					a[ipx, jpx] = popt[0]
					alpha[ipx, jpx] = popt[1]
					beta[ipx, jpx] = popt[2]
					# plot ramp beginning if pixel is selected
 					if [jpx, ipx] in pixlist:
						# find SG number, i and j are flipped in usage
						if jpx < 2048 and ipx < 2048:
							iSG = 3
						elif jpx < 2048 and ipx > 2047:
							iSG = 2
						elif jpx > 2047 and ipx > 2047:
							iSG = 1
						else:
							iSG = 0
						ap = popt[0]
						alphap = popt[1]
						betap = popt[2]
						bp = alphap / betap
						signalpoly = [bp, ap]
						lintimes = np.linspace(0, itimes[linrange][-1] + 2, 100)
						plt.figure()
						plt.plot(itimes[linrange], levels[linrange], 'x', label='Measured')
						plt.plot(lintimes, efunc(lintimes, ap, alphap, betap), label='e func')
						plt.plot(lintimes, np.polyval(signalpoly, lintimes), label='Linear slope')
						plt.grid()
						plt.legend(loc=0)
						plt.title('Single pixel data ramp %s SG%i' %(rmode, iSG+1))
						plt.xlabel('Integration time / s')
						plt.ylabel('Signal / ADU')
						plt.figtext(0.02, 0.03, 'Linear: slope %5.1f, intercept %5.2f' %(bp, ap), ha='left', style='italic', size=8)
						plt.figtext(0.02, 0.01, 'Pixel %i, %i' %(jpx+1, ipx+1), ha='left', style='italic', size=8)
						plt.figtext(0.98, 0.01, 'Data: DET_FLAT_3_3_asrun20141101', ha='right', style='italic', size=8)
						filename = 'Efunc_%s_SG%i_%04i_%04i' %(rmode, iSG+1, jpx+1, ipx+1)
						plt.savefig(os.path.join(outputpath, filename + '.png'))
						plt.close()

	b = alpha / beta
	signalpoly = np.dstack([b, a])
	pr('# Saving linear extrapolation')
	hdu = fits.PrimaryHDU(np.rollaxis(signalpoly, 2))
	filename = 'Linextrapolation_%s_0002' %rmode
	hdu.header['ID'] = filename
	hdu.header['AUTHOR'] = _name + ' ' + _version
	hdu.header['DESCR'] = 'Linear extrapolation for DET_FLAT_3_3 data %s' %rmode
	hdu.header['DATE-OBS'] = (date_obs, 'UTC date of reference data')	
	hdu.header['DATE'] = (datetime.datetime.utcnow().isoformat(), 'UTC date of file creation')
	hdu.header['FILETYPE'] = 'NONLIN intermediate data'
	hdulist = fits.HDUList([hdu])
	pr('# Saving output file %s.fits' %filename)
	hdulist.writeto(os.path.join(outputpath, filename+'.fits'), clobber=True)
	
# plot something about extrapolation
if istep in [0,4]:
	pr('# Plot linear extrapolation data')
	filename = 'Linextrapolation_%s_0002' %rmode	
	hdulist = fits.open(os.path.join(outputpath, filename + '.fits'))
	signalpoly = np.rollaxis(hdulist[0].data, 0, 3)
	b = signalpoly[:,:,0]
	a = signalpoly[:,:,1]

	aflat = a[~np.isnan(a)]
	nnan = np.isnan(a).sum()
	amed = np.median(aflat)
	astd = np.std(aflat)
	plt.figure()
	n, bins, patches = plt.hist(aflat, bins=200, range=[-200, 200], histtype='step')
	nmax = np.argmax(n)
	mode = bins[nmax:nmax+2].sum() / 2
	plt.axvline(mode, label='Mode: %5.2f' %mode, color='r')
	plt.grid()
	plt.legend(loc=0)
	plt.title('Linear approximation fit')
	plt.xlabel('Intercept / ADU')
	plt.ylabel('Number of pixels')
	plt.figtext(0.02, 0.03, r'Median: %5.2f ADU, $\sigma$: %5.2f ADU' %(amed, astd), ha='left', style='italic', size=8)
	plt.figtext(0.02,0.01, 'Non-fitted pixels: %i' %nnan, ha='left', style='italic', size=8)
	filename = 'Linfit_%s_intercept' %rmode
	plt.savefig(os.path.join(outputpath, filename + '.png'))
	plt.close()

	SGcorners = [[0, 2048], [2048, 2048], [2048, 0], [0, 0]]
	fig, axs = plt.subplots(nrows=2, ncols=2)
	plt.figtext(0.02,0.01, 'Non-fitted pixels', ha='left', style='italic', size=8)
	plt.figtext(0.98,0.01, 'Data: DET_FLAT_3_3_asrun20141101', ha='right', style='italic', size=8)
	for iSG in range(4):
		ax = axs.flat[iSG]
		SGc = SGcorners[iSG]
		SGa = a[SGc[0]:SGc[0]+2048, SGc[1]:SGc[1]+2048]
		aflat = SGa[~np.isnan(SGa)]
		nnan = np.isnan(SGa).sum()
		amed = np.median(aflat)
		astd = np.std(aflat)
		n, bins, patches = ax.hist(aflat, bins=200, range=[-200, 200], histtype='step')
		nmax = np.argmax(n)
		mode = bins[nmax:nmax+2].sum() / 2
		ax.axvline(mode, label='Mode: %5.2f' %mode, color='r')
		ax.grid()
		ax.legend(loc=7)
		ax.set_title('Linear approximation SG%i' %(iSG+1))
		ax.set_xlabel('Intercept / ADU')
		ax.set_ylabel('Number of pixels')
		plt.figtext(0.14+iSG*0.1,0.01, 'SG%i: %i' %(iSG+1, nnan), ha='left', style='italic', size=8)
	plt.tight_layout()
	filename = 'Linfit_%s_intercept_SGs' %rmode
	plt.savefig(os.path.join(outputpath, filename + '.png'))
	plt.savefig(os.path.join(outputpath, filename + '.pdf'))
	plt.close()
	
	# plot nonlinear residual and full ramp of single pixels
	pr('# Plotting some pixels\' linear residuals and ramps')
	# 4 random pixels per SG
	npx = 4
	np.random.seed(10)
	# as defined below, 1st is j, 2nd is i (nice selection)
	pxys = np.random.randint(4, 2044, (npx,2))
	SGcorners = [[0, 2048], [2048, 2048], [2048, 0], [0, 0]]
	filebase = 'DET_FLAT_'
	nIDs = len(nIDrange)
	istartlist = [1] * 35
	nexps = 10
	for iSG in range(4):
		for ipx in range(npx):
			px = SGcorners[iSG][1] + pxys[ipx, 1]
			py = SGcorners[iSG][0] + pxys[ipx, 0]
			pr('  * pixel %i, %i' %(px+1, py+1))
			# get data vectors
			meddata = np.zeros(nIDs)
			itimes = np.zeros(nIDs)
			for iID in range(nIDs):
				nID = nIDrange[iID]
				file = filebase+'%02i_CDS_medclip0002-0010.fits' %(nID)
				hdulist = fits.open(os.path.join(inputpath, file))
				data = hdulist[0].data.astype('int32')
				meddata[iID] = data[py, px]
				itimes[iID] = hdulist[0].header['ITIME']
			# calculate linear signal and relative residual
			ap = a[py, px]
			bp = b[py, px]
			if np.isnan(ap):
				continue
			lindata = np.polyval([bp, ap], itimes)
			linres = (lindata - meddata) / lindata
			# Plot residuals
			plt.figure()
			plt.plot(meddata, linres * 100, 'x', label='Relative residual')
			plt.ylim(ymax = 30)
			plt.legend(loc=0)
			plt.grid()
			plt.title('Single pixel nonlinear residual %s SG%i' %(rmode, iSG+1))
			plt.xlabel('Measured signal / ADU')
			plt.ylabel('Residual relative to linear extrapolation / %')
			plt.figtext(0.02, 0.01, 'Pixel %i, %i' %(px+1, py+1), ha='left', style='italic', size=8)
			plt.figtext(0.98, 0.01, 'Data: DET_FLAT_3_3_asrun20141101', ha='right', style='italic', size=8)
			filename = 'Nonlinres_%s_SG%i_%04i_%04i' %(rmode, iSG+1, px+1, py+1)
			plt.savefig(os.path.join(outputpath, filename + '.png'))
			plt.close()

			# Plot ramps
			lintimes = np.linspace(0, itimes[-1] + 2, 100)
			plt.figure()
			plt.plot(itimes, meddata, 'x', label='Measured')
			plt.plot(lintimes, np.polyval([bp, ap], lintimes), 'r', label='Linear slope')
			plt.ylim(ymin = np.floor(ap/100)*100)
			plt.legend(loc=0)
			plt.grid()
			plt.title('Single pixel data ramp %s SG%i' %(rmode, iSG+1))
			plt.xlabel('Integration time / s')
			plt.ylabel('Signal / ADU')
			plt.figtext(0.02, 0.03, 'Linear: slope %5.1f, intercept %5.2f' %(bp, ap), ha='left', style='italic', size=8)
			plt.figtext(0.02, 0.01, 'Pixel %i, %i' %(px+1, py+1), ha='left', style='italic', size=8)
			plt.figtext(0.98, 0.01, 'Data: DET_FLAT_3_3_asrun20141101', ha='right', style='italic', size=8)
			filename = 'Ramplin_%s_SG%i_%04i_%04i' %(rmode, iSG+1, px+1, py+1)
			plt.savefig(os.path.join(outputpath, filename + '.png'))
			plt.close()

	# plot residual median of all pixels
	pr('# Plotting median linear residuals')
	# get data vectors
	medres = np.zeros(nIDs)
	meddata = np.zeros(nIDs)
	stddata = np.zeros(nIDs)
	stdres = np.zeros(nIDs)
	for iID in range(nIDs):
		nID = nIDrange[iID]
		print 'File ',nID
		file = filebase+'%02i_CDS_medclip0002-0010.fits' %(nID)
		hdulist = fits.open(os.path.join(inputpath, file))
		data = hdulist[0].data.astype('int32')
		itime = hdulist[0].header['ITIME']
		# calculate linear signal and relative residual, only valid pixels
		lindata = a + b * itime
		linres = (lindata - data) / lindata
		pixelmask = ~np.isnan(linres)
		medres[iID] = np.median(linres[pixelmask])
		#stdres[iID] = np.std(linres[pixelmask])
		meddata[iID] = np.median(data[pixelmask])
		stddata[iID] = np.std(data[pixelmask])
	# Plot data
	plt.figure()
	#plt.plot(meddata, medres * 100, 'x', label='Relative residual')
	plt.errorbar(meddata, medres*100, xerr=stddata, fmt='x', label='Relative residual')
	plt.ylim(0, 30)
	plt.legend(loc=0)
	plt.grid()
	plt.title('Median nonlinear residual %s' %(rmode))
	plt.xlabel('Median measured signal / ADU')
	plt.ylabel('Median residual relative to linear extrapolation / %')
	plt.figtext(0.98, 0.01, 'Data: DET_FLAT_3_3_asrun20141101', ha='right', style='italic', size=8)
	filename = 'Nonlinres_%s_median' %(rmode)
	plt.savefig(os.path.join(outputpath, filename + '.png'))
	plt.close()
	 

# fit polynomials and get best one
if istep in [0,5]:
	pr('# Finding best polynomial fit')
	filename = 'Linextrapolation_%s_0002' %rmode	
	hdulist = fits.open(os.path.join(outputpath, filename + '.fits'))
	signalpoly = np.rollaxis(hdulist[0].data, 0, 3)
	datalist = []
	itimes = np.zeros(nIDs)
	# load data
	pr('# Loading data')
	for iID in range(nIDs):
		nID = nIDrange[iID]
		pr('  * Processing image number %i' %nID)
		pathlist = os.listdir(inputpath)
		fitsfiles = fnmatch.filter(pathlist, filebase+'%02i_CDS_medclip0002-0010.fits' %(nID))
		if len(fitsfiles) != 1:
			raise FileError('More than one file found for image number %i' %iID)
		# load data, get median
		hdulist = fits.open(os.path.join(inputpath, fitsfiles[0]))
		data = hdulist[0].data
		datalist.append(data)
		itimes[iID] = hdulist[0].header['ITIME']
		date_obs = hdulist[0].header['DATE-OBS']
	signals = np.dstack(datalist)
	datalist = 0

	# plot 4 random pixels per SG
	npx = 4
	np.random.seed(10)
	# as defined below, 1st is j, 2nd is i (nice selection)
	pxys = np.random.randint(4, 2044, (npx,2))
	SGcorners = [[0, 2048], [2048, 2048], [2048, 0], [0, 0]]
	# expand to all SGs and as list for comparison
	pixlist = []
	for iSG in range(4):
		for ipx in range(npx):
			px = SGcorners[iSG][1] + pxys[ipx, 1]
			py = SGcorners[iSG][0] + pxys[ipx, 0]
			# list has correct order
			pixlist.append([px, py])
	# fit polynomial from 10 to maximum number of points
	npts = signals.shape[2]
	minpts = 10
	ipts = np.arange(minpts, npts+1)
	# cube of linear signals
	pr('# Caclulating linear signal values')
	linsignals = signals * 0
	for itime in range(npts):
		linsignals[:, :, itime] = polyval_map_offset(signalpoly, np.ones((4096, 4096)) * itimes[itime])	
	# Fitting polynomials
	nlpolys = np.zeros((4096, 4096, porder))
	nlmaxs = np.zeros((4096, 4096))
	pr('# Fitting polynomials per pixel')
	pingsteps = (np.arange(1,8) * 512) - 1
	for ipx in range(4096):
		if ipx in pingsteps:
			print '  * ipx %i' %(ipx+1)
		for jpx in range(4096):
			# skip pixel without linear extrapolation: invalid correction
			if np.isnan(signalpoly[ipx, jpx, 0]):
				nlpolys[ipx, jpx, :] = [0, 0, 0, 1]
				nlmaxs[ipx, jpx] = np.nan
				continue
			for ipt in ipts[::-1]:
				# skip if last point is > 98% saturation
				if signals[ipx, jpx, ipt-1] > signals[ipx, jpx, -1] * 0.98:
					continue
				nlpoly = np.polyfit(signals[ipx, jpx, 0:ipt], linsignals[ipx, jpx, 0:ipt], porder)
				# relative residual of all points
				relerror = (np.polyval(nlpoly, signals[ipx, jpx, :]) - linsignals[ipx, jpx, :]) / linsignals[ipx, jpx, :]
				# mean residual of used points, skip first ones
				if rmode == 'lir':
					resmean = relerror[2:ipt].mean()
					resstd = relerror[2:ipt].std()
				elif rmode == 'rrr-mpia':
					resmean = relerror[1:ipt].mean()
					resstd = relerror[1:ipt].std()				
				# find optimum fit: reduce number until mean res < 0.002 and std < 0.008
				if np.abs(resmean) < 0.002 and resstd < 0.008:
					# skip super-corrected pixels: large linear signal
					correction = linsignals[ipx, jpx, 0:ipt] / signals[ipx, jpx, 0:ipt]
					if np.any(correction > 1.5):
						nlpolys[ipx, jpx, :] = [0, 0, 0, 1]
						nlmaxs[ipx, jpx] = np.nan
					else:
						nlpolys[ipx, jpx, :] = nlpoly[:-1]
						nlmaxs[ipx, jpx] = signals[ipx, jpx, ipt-1]
						# Plot fit of some pixels
						if [jpx, ipx] in pixlist:
							# find SG number, i and j are flipped in usage
							if jpx < 2048 and ipx < 2048:
								iSG = 3
							elif jpx < 2048 and ipx > 2047:
								iSG = 2
							elif jpx > 2047 and ipx > 2047:
								iSG = 1
							else:
								iSG = 0
							plt.figure()
							plt.plot(signals[ipx, jpx, :], linsignals[ipx, jpx, :], 'x', label='Data')
							plt.plot(signals[ipx, jpx, :], np.polyval(nlpoly, signals[ipx, jpx, :]), label='Polyfit')
							plt.axvline(nlmaxs[ipx, jpx], ls='--', c='r', label='Fit limit')
							plt.legend(loc='upper left')
							plt.grid()
							plt.title('Single pixel nonlinearity correction fit %s SG%i' %(rmode, iSG+1))
							plt.xlabel('Measured signal / ADU')
							plt.ylabel('Linear signal / ADU')
							plt.figtext(0.02, 0.03, 'Pixel %i, %i' %(jpx+1, ipx+1), ha='left', style='italic', size=8)
							plt.figtext(0.02,0.01, 'Max. correctable signal: %6i ADU, max true signal: %7.1f ADU' %(nlmaxs[ipx, jpx], np.polyval(nlpoly, nlmaxs[ipx, jpx])), ha='left', style='italic', size=8)
							plt.figtext(0.98,0.03, 'Polynmial order: %i' %(porder), ha='right', style='italic', size=8)
							plt.figtext(0.98, 0.01, 'Data: DET_FLAT_3_3_asrun20141101', ha='right', style='italic', size=8)
							filename = 'Nonlinfit_poly_%s_SG%i_%04i_%04i' %(rmode, iSG+1, jpx+1, ipx+1)
							plt.savefig(os.path.join(outputpath, filename + '.png'))
							plt.close()

							# Plot relative residuals
							plt.figure()
							plt.plot(signals[ipx, jpx, :], relerror, 'x', label='Relative residual')
							plt.axhline(0, c='g')
							plt.axvline(nlmaxs[ipx, jpx], ls='--', c='r', label='Fit limit')
							plt.legend(loc='lower left')
							plt.grid()
							plt.title('Single pixel nonlinearity correction fit residuals %s SG%i' %(rmode, iSG+1))
							plt.xlabel('Measured signal / ADU')
							plt.ylabel('Relative fit residual')
							plt.figtext(0.02,0.01, 'Polynmial order: %i, max. correctable signal: %6i ADU' %(porder, nlmaxs[ipx, jpx]), ha='left', style='italic', size=8)
							plt.figtext(0.02, 0.03, 'Pixel %i, %i' %(jpx+1, ipx+1), ha='left', style='italic', size=8)
							plt.figtext(0.98,0.03, 'Relative fit residual (%%): %4.2f +- %4.2f' %(resmean*100, resstd*100), ha='right', style='italic', size=8)
							plt.figtext(0.98, 0.01, 'Data: DET_FLAT_3_3_asrun20141101', ha='right', style='italic', size=8)
							filename = 'Nonlinfit_resid_%s_SG%i_%04i_%04i' %(rmode, iSG+1, jpx+1, ipx+1)
							plt.savefig(os.path.join(outputpath, filename + '.png'))
							plt.close()
						
					break
				else:
					continue
			else:
				# no fit found: invalid correction
				nlpolys[ipx, jpx, :] = [0, 0, 0, 1]
				nlmaxs[ipx, jpx] = np.nan
				
	pr('# Saving nonlinear correction data')
	hdu = fits.PrimaryHDU()
	filename = 'NONLIN_%s_0002' %rmode.upper()
	hdu.header['ID'] = filename
	hdu.header['AUTHOR'] = _name + ' ' + _version
	hdu.header['DESCR'] = 'Non-linearity correction data %s mode' %rmode
	hdu.header['FILETYPE'] = 'NONLINCORR_%s' %rmode.upper()
	hdu.header['USE_AFT'] = ('2014-10-27', 'Use for data taken after this date')
	hdu.header['DATE-OBS'] = (date_obs, 'UTC date of reference data')	
	hdu.header['DATE'] = (datetime.datetime.utcnow().isoformat(), 'UTC date of file creation')
	# add saturation map and polynomial in extensions
	extname = 'LINMAX'
	maphdu = fits.ImageHDU(nlmaxs.astype('float32'), name=extname)
	maphdu.header['BUNIT'] = 'ADU'
	maphdu.header['DESCR'] = 'Max level for linearity correction'
	extname = 'LINPOLY'
	polyhdu = fits.ImageHDU(np.rollaxis(nlpolys, 2).astype('float32'), name=extname)
	polyhdu.header['DESCR'] = 'Polynomial coefficients (highest first), no offset'
	hdulist = fits.HDUList([hdu, maphdu, polyhdu])
	pr('# Saving output file %s.fits' %filename)
	hdulist.writeto(os.path.join(outputpath, filename+'.fits'), clobber=True)

# Lower correction limit by 2%
if istep in [0,5.1]:
	pr('# Adjust correction limit')
	filename = 'NONLIN_%s_0002' %rmode.upper()
	hdulist = fits.open(os.path.join(outputpath, filename + '.fits'))
	nlmaxs = hdulist['LINMAX'].data
	hdulist['LINMAX'].data = nlmaxs / 0.98 * 0.96
	filename = 'NONLIN_%s_0003' %rmode.upper()
	hdulist[0].header['ID'] = filename
	hdulist[0].header['AUTHOR'] = _name + ' ' + _version
	hdulist[0].header['USE_AFT'] = ('2014-10-27', 'Use for data taken after this date')
	hdulist[0].header['DATE'] = (datetime.datetime.utcnow().isoformat(), 'UTC date of file creation')
	pr('# Saving output file %s.fits' %filename)
	hdulist.writeto(os.path.join(outputpath, filename+'.fits'), clobber=True)

# Plot fit info
if istep in [0,6]:
	pr('# Plot nonlinearity correction data')
	filename = 'NONLIN_%s_0003' %rmode.upper()
	hdulist = fits.open(os.path.join(outputpath, filename + '.fits'))
	nlmaxs = hdulist['LINMAX'].data
	nlpolys = np.rollaxis(hdulist['LINPOLY'].data, 0, 3)
	SGcorners = [[0, 2048], [2048, 2048], [2048, 0], [0, 0]]

	# Correction maximum
	fig, axs = plt.subplots(nrows=2, ncols=2)
	plt.figtext(0.02,0.01, 'Non-correctable pixels', ha='left', style='italic', size=8)
	plt.figtext(0.98,0.01, 'Data: DET_FLAT_3_3_asrun20141101', ha='right', style='italic', size=8)
	for iSG in range(4):
		ax = axs.flat[iSG]
		SGc = SGcorners[iSG]
		SGa = nlmaxs[SGc[0]+4:SGc[0]+2044, SGc[1]+4:SGc[1]+2044]
		aflat = SGa[~np.isnan(SGa)]
		nnan = np.isnan(SGa).sum()
		amed = np.median(aflat)
		astd = np.std(aflat)
		n, bins, patches = ax.hist(aflat/1000, bins=200, histtype='step', log=True)
		nmax = np.argmax(n)
		mode = bins[nmax:nmax+2].sum() / 2
		ax.axvline(mode, label='Mode: %5.2f' %mode, color='r')
		ax.text(0.5, 0.93, '%i' %(mode*1000), ha='center', va='center', color='r', transform = ax.transAxes)
		ax.grid()
		ax.set_title('Correction limit SG%i' %(iSG+1))
		ax.set_xlabel(r'Signal / $10^3$ ADU')
		ax.set_ylabel('Number of pixels')
		plt.figtext(0.18+iSG*0.1,0.01, 'SG%i: %i' %(iSG+1, nnan), ha='left', style='italic', size=8)
	plt.tight_layout()
	filename = 'Nonlin_%s_maxsignal_SGs' %rmode
	plt.savefig(os.path.join(outputpath, filename + '.png'))
	plt.savefig(os.path.join(outputpath, filename + '.pdf'))
	plt.close()
	
	# Polynomial coefficients
	coeffs = [4, 3, 2, 1]
	for icoeff in range(4):
		fig, axs = plt.subplots(nrows=2, ncols=2)
		plt.figtext(0.98,0.01, 'Data: DET_FLAT_3_3_asrun20141101', ha='right', style='italic', size=8)
		for iSG in range(4):
			ax = axs.flat[iSG]
			SGc = SGcorners[iSG]
			SGa = nlpolys[SGc[0]+4:SGc[0]+2044, SGc[1]+4:SGc[1]+2044, icoeff]
			aflat = SGa[~np.isnan(SGa)]
			amed = np.median(aflat)
			astd = np.std(aflat)
			oom = int(np.log10(astd*2))
			scale = 10**oom
			n, bins, patches = ax.hist(aflat/scale, bins=200, histtype='step', log=True, range=[(amed-5*astd)/scale, (amed+5*astd)/scale])
			nmax = np.argmax(n)
			mode = bins[nmax:nmax+2].sum() / 2
			ax.axvline(amed/scale, label='Median: %5.2f' %amed, color='r')
			ax.text(0.70, 0.93, '%g' %(amed), ha='center', va='center', color='r', transform = ax.transAxes)
			ax.grid()
			ax.set_title('Polynomial data SG%i' %(iSG+1))
			ax.set_xlabel(r'$c_{%i}$ / $10^{%i}$' %(coeffs[icoeff], oom))
			ax.set_ylabel('Number of pixels')
		plt.tight_layout()
		filename = 'Nonlin_%s_coeff%i_SGs' %(rmode, coeffs[icoeff])
		plt.savefig(os.path.join(outputpath, filename + '.png'))
		plt.savefig(os.path.join(outputpath, filename + '.pdf'))
		plt.close()
	
	# Compare max correction with saturation in data (last file)
	nID = nIDrange[-1]
	pathlist = os.listdir(inputpath)
	fitsfiles = fnmatch.filter(pathlist, filebase+'%02i_CDS_medclip0002-0010.fits' %(nID))
	# load data
	hdulist = fits.open(os.path.join(inputpath, fitsfiles[0]))
	data = hdulist[0].data
	satfraction = nlmaxs / data
	# Correction maximum relative to saturation
	fig, axs = plt.subplots(nrows=2, ncols=2)
	plt.figtext(0.02,0.01, 'Non-correctable pixels', ha='left', style='italic', size=8)
	plt.figtext(0.98,0.01, 'Data: DET_FLAT_3_3_asrun20141101', ha='right', style='italic', size=8)
	for iSG in range(4):
		ax = axs.flat[iSG]
		SGc = SGcorners[iSG]
		SGa = satfraction[SGc[0]+4:SGc[0]+2044, SGc[1]+4:SGc[1]+2044]
		aflat = SGa[~np.isnan(SGa)]
		nnan = np.isnan(SGa).sum()
		n, bins, patches = ax.hist(aflat, bins=200, histtype='step', cumulative=True, normed=True, log=True)
		ax.set_xlim([0, 1])
		ax.grid()
		ax.set_title('Correction limit SG%i' %(iSG+1))
		ax.set_xlabel(r'Signal relative to saturation')
		ax.set_ylabel('Cumulative fraction')
		plt.figtext(0.18+iSG*0.1,0.01, 'SG%i: %i' %(iSG+1, nnan), ha='left', style='italic', size=8)
	plt.tight_layout()
	filename = 'Nonlin_%s_maxsignal_rel_SGs' %rmode
	plt.savefig(os.path.join(outputpath, filename + '.png'))
	plt.savefig(os.path.join(outputpath, filename + '.pdf'))
	plt.close()

	# True correction maximum (measured maximum corrected)
	corrmax = polyval_map(nlpolys, nlmaxs)
	fig, axs = plt.subplots(nrows=2, ncols=2)
	plt.figtext(0.02,0.01, 'Non-correctable pixels', ha='left', style='italic', size=8)
	plt.figtext(0.98,0.01, 'Data: DET_FLAT_3_3_asrun20141101', ha='right', style='italic', size=8)
	for iSG in range(4):
		ax = axs.flat[iSG]
		SGc = SGcorners[iSG]
		SGa = corrmax[SGc[0]+4:SGc[0]+2044, SGc[1]+4:SGc[1]+2044]
		aflat = SGa[~np.isnan(SGa)]
		nnan = np.isnan(SGa).sum()
		amed = np.median(aflat)
		astd = np.std(aflat)
		n, bins, patches = ax.hist(aflat/1000, bins=200, histtype='step', log=True)
		nmax = np.argmax(n)
		mode = bins[nmax:nmax+2].sum() / 2
		ax.axvline(mode, label='Mode: %5.2f' %mode, color='r')
		ax.text(0.5, 0.93, '%i' %(mode*1000), ha='center', va='center', color='r', transform = ax.transAxes)
		ax.grid()
		ax.set_title('True correction limit SG%i' %(iSG+1))
		ax.set_xlabel(r'Signal / $10^3$ ADU')
		ax.set_ylabel('Number of pixels')
		plt.figtext(0.18+iSG*0.1,0.01, 'SG%i: %i' %(iSG+1, nnan), ha='left', style='italic', size=8)
	plt.tight_layout()
	filename = 'Nonlin_%s_maxsignal_true_SGs' %rmode
	plt.savefig(os.path.join(outputpath, filename + '.png'))
	plt.savefig(os.path.join(outputpath, filename + '.pdf'))
	plt.close()

# Fix header and save as MEF file
if istep in [0, 7]:
	pr('# Saving as MEF output')
	# load data
	filename = 'NONLIN_%s_0003' %rmode.upper()
	hdulist = fits.open(os.path.join(outputpath, filename + '.fits'))
	nlmaxs = hdulist['LINMAX'].data
	nlpolys = np.rollaxis(hdulist['LINPOLY'].data, 0, 3)
	SGcorners = [[0, 2048], [2048, 2048], [2048, 0], [0, 0]]
	# Load header of first calibration exposure
	nID = nIDrange[0]
	pathlist = os.listdir(inputpath)
	fitsfiles = fnmatch.filter(pathlist, filebase+'%02i_CDS_medclip0002-0010.fits' %(nID))
	inheader = fits.getheader(os.path.join(inputpath, fitsfiles[0]))
	# hard-coded here: first and last input FILE_ID
	if rmode == 'rrr-mpia':
		firstID = 'Panic.2014-11-01T17:57:54.379_0001_001'
		lastID = 'Panic.2014-11-02T21:06:44.025_0019_001'
	elif rmode == 'lir':
		firstID = 'Panic.2014-11-02T02:16:23.496_0001_001'
		lastID = 'Panic.2014-11-03T00:43:12.606_0019_001'

	# Save in MEF file per SG
	pr('# Saving nonlinear correction data')
	hdu = fits.PrimaryHDU()
	filename = 'mNONLIN_%s_01.01' %rmode.upper()
	hdu.header['ID'] = filename
	hdu.header['AUTHOR'] = 'B. Dorner'
	hdu.header['DESCR'] = 'Non-linearity correction data %s mode' %rmode
	hdu.header['INSTRUME'] = 'PANIC'
	hdu.header['PAPITYPE'] = ('MASTER_LINEARITY', 'File data type as classified by the pipeline')
	hdu.header['DATE'] = (datetime.datetime.utcnow().isoformat(), 'UTC date of file creation')
	hdu.header['USE_AFT'] = ('2014-10-27', 'Use for data taken after this date')
	hdu.header['DETROT90'] = (inheader['DETROT90'], inheader.comments['DETROT90'])
	hdu.header['DETXYFLI'] = (inheader['DETXYFLI'], inheader.comments['DETXYFLI'])
	hdu.header['PREAD'] = (inheader['PREAD'], inheader.comments['PREAD'])
	hdu.header['PSKIP'] = (inheader['PSKIP'], inheader.comments['PSKIP'])
	hdu.header['LSKIP'] = (inheader['LSKIP'], inheader.comments['LSKIP'])
	hdu.header['READMODE'] = (inheader['READMODE'], inheader.comments['READMODE'])
	hdu.header['IDLEMODE'] = ('wait', inheader.comments['IDLEMODE'])
	hdu.header['IDLETYPE'] = (inheader['IDLETYPE'], inheader.comments['IDLETYPE'])
	cards = ['B_EXT', 'B_DSUB', 'B_VREST', 'B_VBIAG']
	for card in cards:
		hdu.header['%s1'%card] = (inheader['%s1'%card], inheader.comments['%s1'%card])
		hdu.header['%s2'%card] = (inheader['%s2'%card], inheader.comments['%s2'%card])
		hdu.header['%s3'%card] = (inheader['%s3'%card], inheader.comments['%s3'%card])
		hdu.header['%s4'%card] = (inheader['%s4'%card], inheader.comments['%s4'%card])
	hdu.header['HISTORY'] = 'Description of creation'
	hdu.header['HISTORY'] = 'DOCUMENT:'
	hdu.header['HISTORY'] = 'PANIC-DET-TN-02_1_0'
	hdu.header['HISTORY'] = 'SOFTWARE:'
	hdu.header['HISTORY'] =  _name + ' ' + _version
	hdu.header['HISTORY'] = 'DATA:'
	hdu.header['HISTORY'] = 'First FILE_ID: '+ firstID
	hdu.header['HISTORY'] = 'Last FILE_ID: '+ lastID
	hdu.header['HISTORY'] = inheader['CREATOR']
	hdu.header['HISTORY'] = 'DIFFERENCES:'
	hdu.header['HISTORY'] = 'Reduced max. correction limit'
	# add saturation map and polynomial in extensions
	hdus = [hdu]
	for iSG in range(1, 5):
		SGc = SGcorners[iSG-1]
		extname = 'LINMAX%i' %iSG
		maphdu = fits.ImageHDU(nlmaxs[SGc[0]:SGc[0]+2048, SGc[1]:SGc[1]+2048].astype('float32'), name=extname)
		maphdu.header['BUNIT'] = 'ADU'
		maphdu.header['DESCR'] = 'Max level for linearity correction'
		maphdu.header['DETSEC'] = '[%i:%i,%i:%i]' %(SGc[1]+1, SGc[1]+2048, SGc[0]+1, SGc[0]+2048)
		maphdu.header['DET_ID'] = 'SG%i' %iSG
		hdus.append(maphdu)
	for iSG in range(1, 5):
		SGc = SGcorners[iSG-1]
		extname = 'LINPOLY%i' %iSG
		polyhdu = fits.ImageHDU(np.rollaxis(nlpolys[SGc[0]:SGc[0]+2048, SGc[1]:SGc[1]+2048, :], 2).astype('float32'), name=extname)
		polyhdu.header['DESCR'] = 'Polynomial coefficients (highest first), no offset'
		polyhdu.header['DETSEC'] = '[%i:%i, %i:%i]' %(SGc[1]+1, SGc[1]+2048, SGc[0]+1, SGc[0]+2048)
		polyhdu.header['DETID'] = 'SG%i' %iSG
		hdus.append(polyhdu)
	hdulist = fits.HDUList(hdus)
	pr('# Saving output file %s.fits' %filename)
	hdulist.writeto(os.path.join(outputpath, filename+'.fits'), clobber=True)

# Plot correction limit image
if istep in [0, 8]:
	pr('# Creating correction limit image')
	# load data
	filename = 'NONLIN_%s_0003' %rmode.upper()
	hdulist = fits.open(os.path.join(outputpath, filename + '.fits'))
	nlmaxs = hdulist['LINMAX'].data
	figure = plt.figure()
	plt.axes()
	axes = figure.gca()
	axes.set_aspect('equal')
	plt.axes(axisbg='r')
	plt.imshow(nlmaxs, vmin=0, vmax=55000)
	plt.set_cmap('gray')
	cbar = plt.colorbar()
	plt.title('Correction limit %s' %rmode)
	plt.xlabel('Pixel i')
	plt.ylabel('Pixel j')
	cbar.set_label('Pixel value / ADU')
	plt.figtext(0.02,0.01, 'Non-correctable pixels in red', ha='left', style='italic', size=8)
	plt.figtext(0.98,0.01, 'Data: DET_FLAT_3_3_asrun20141101', ha='right', style='italic', size=8)	
	plt.tight_layout()
	filename = 'Nonlin_%s_maxsignal_img' %rmode
	plt.savefig(os.path.join(outputpath, filename + '.png'), dpi=200)
	plt.savefig(os.path.join(outputpath, filename + '.pdf'))
	plt.close()

# Create bad pixel map for GEIRS from non-correctable pixels
if istep in [0, 9]:
	pr('# Creating GEIRS bad pixel file')
	# load data
	filename = 'NONLIN_%s_0003' %rmode.upper()
	hdulist = fits.open(os.path.join(outputpath, filename + '.fits'))
	nlmaxs = hdulist['LINMAX'].data
	useaft = hdulist[0].header['USE_AFT']
	# create bad pixel file, replace existing one
	badfile = open(os.path.join(outputpath, 'badpixels.panic.%s-%s' %(rmode, useaft)), 'w')
	# use all nan as bad pixels, write to file
	for i in range(4096):
		for j in range(4096):
			if np.isnan(nlmaxs[j, i]):
				badfile.write('%i\t%i\n' %(i+1, j+1))
	badfile.close()
	

