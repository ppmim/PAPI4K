#!/usr/bin/env python
#########################################################################
# PANIC data
#########################################################################
# Test nonlinearity correction data with different data
# Inputs:
# - data from FLAT_3_4
#
# usage: p_56_cyc9_test_nonlinearity.py [-h] [--nolog]
#                                       {rrr-mpia,lir} {1}
#                                       {medavg,calc,plot,corr,resid,plotresid,all}
# 
# positional arguments:
#   {rrr-mpia,lir}        Readout mode string
#   {1}                   Data to test: (1)Sat. 30s lir
#   {medavg,calc,plot,corr,resid,plotresid,all}
#                         Step: Median average, calculate data, plot,
#                         correlation, residuals, plot resid., all
# 
# optional arguments:
#   -h, --help            show this help message and exit
#   --nolog               Do not write output log file
#
# 1.0 11/05/2015 BD Creation from p_48_test_nonlinearity 1.5.1
# 1.0.1 12/05/2015 BD Update
#	1) Corrected histogram image output w/o matplotlibrc settings
# 1.1 12/05/2015 BD Update
#	1) Added data rrr-mpia flat 3.4
#
_name = 'p_56_cyc9_test_nonlinearity.py'
_version = '1.1'
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
import sys
sys.path.append('lib')
try:
	import f_linearity
except ImportError:
	print 'Cannot import f_linearity, some functions may not work!'

# parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('rmode', type=str, choices=['rrr-mpia', 'lir'], help='Readout mode string')
arghelp = 'Data to test: (1)Sat. 30s'
parser.add_argument('itype', type=int, choices=[1], help=arghelp)
parser.add_argument('step', type=str, choices=['medavg', 'calc', 'plot', 'corr', 'resid'
, 'plotresid', 'all'], help='Step: Median average, calculate data, plot, correlation, residuals, plot resid., all')
parser.add_argument('--nolog', help='Do not write output log file', action='store_true')
args = parser.parse_args()
rmode = args.rmode
itype = args.itype
step = args.step
writelog = not args.nolog

# path to data
nonlinpath = 'output/47_cyc7_nonlinearity_data_%s' %rmode
outputpath = 'output/56_cyc9_test_nonlinearity'
# parameters of the files
if rmode == 'rrr-mpia':
	if itype == 1:
		nIDrange = range(33, 65)
		filebase = ['DET_FLAT_', '_CDS_medclip0001-0010']
		folder = '2015-05-11_flat_3_4'
		istartlist = [1] * len(nIDrange)
		nexps = 10
		# path to data
		import socket
		hostname = socket.gethostname()
		if hostname.startswith('panic'):
			# panicXX
			archivepath = '/data1/PANIC/'
			inputpath = '/data2/out_panic/2015-05-11_flat_3_4'
		elif hostname == 'aida43216':
			inputpath = '/home/dorner/work/PANIC/processed/2015-05-11_flat_3_4'
		else:
			inputpath = '/Users/dorner/work/PANIC/Exposures/processed/2015-05-11_flat_3_4'
# 	elif itype == 2:
# 		nIDrange = range(1, 33)
# 		filebase = ['DET_FLAT_', '_medclip0001-0010']
# 		inputpath = 'output/40_cyc6_medianclip'
	# maximum signal as last file in calibration data
	maxsignalfile = os.path.join('/home/dorner/work/PANIC/processed/2014-11-01_flat_3_3', 'DET_FLAT_66_CDS_medclip0002-0010.fits')
elif rmode == 'lir':
	if itype == 1:
		nIDrange = range(1, 33)
		filebase = ['DET_FLAT_', '_CDS_medclip0001-0010']
		folder = '2015-05-11_flat_3_4'
		istartlist = [1] * len(nIDrange)
		nexps = 10
		# path to data
		import socket
		hostname = socket.gethostname()
		if hostname.startswith('panic'):
			# panicXX
			archivepath = '/data1/PANIC/'
			inputpath = '/data2/out_panic/2015-05-11_flat_3_4'
		elif hostname == 'aida43216':
			inputpath = '/home/dorner/work/PANIC/processed/2015-05-11_flat_3_4'
		else:
			inputpath = '/Users/dorner/work/PANIC/Exposures/processed/2015-05-11_flat_3_4'
# 	elif itype == 2:
# 		nIDrange = range(33, 65)
# 		filebase = ['DET_FLAT_', '_medclip0001-0010']
# 		inputpath = 'output/40_cyc6_medianclip'
	# maximum signal as last file in calibration data
	maxsignalfile = os.path.join('/home/dorner/work/PANIC/processed/2014-11-01_flat_3_3', 'DET_FLAT_70_CDS_medclip0002-0010.fits')
nIDs = len(nIDrange)
datatype = ['Sat030s'][itype-1]
datasource = ['DET_FLAT_3_4_asrun20150511'][itype-1]

if not os.access(outputpath,os.F_OK):
	os.mkdir(outputpath)

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

def pearsonr(x, y):
	'''Pearson correlation with masked arrays, correlation along last axis'''
	n = x.shape[-1]
	if y.shape[-1] != n:
		raise ValueError('Inequal input array sizes')
	x = np.ma.masked_array(x)
	y = np.ma.masked_array(y)
	mask = np.ma.mask_or(x.mask, y.mask)
	x.mask = mask
	y.mask = mask
	sx = x.sum(axis=-1)
	sy = y.sum(axis=-1)
	a = n * np.sum(x * y, axis=-1) - sx * sy
	b = np.sqrt(n * np.sum(x**2, axis=-1) - sx**2) * np.sqrt(n * np.sum(y**2, axis=-1) - sy**2)
	return a / b

def pearsonr_map(x, y):
	'''Pearson correlation with 1D vector and masked 3D array, correlation along third axis'''
	n = x.size
	if y.shape[2] != n:
		raise ValueError('Inequal input array sizes')
	y = np.ma.masked_array(y)
	# create cube with x vector in third axis
	x = (y * 0) + x[np.newaxis, np.newaxis, :]
	sx = x.sum(axis=-1)
	sy = y.sum(axis=-1)
	a = n * np.sum(x * y, axis=-1) - sx * sy
	b = np.sqrt(n * np.sum(x**2, axis=-1) - sx**2) * np.sqrt(n * np.sum(y**2, axis=-1) - sy**2)
	return a / b

def linregression_map(x, y):
	'''Linear least-squares regression with masked arrays along last axis'''
	n = x.shape[-1]
	if y.shape[-1] != n:
		raise ValueError('Inequal input array sizes')
	xm = np.ma.masked_array(x)
	ym = np.ma.masked_array(y)
	mask = np.ma.mask_or(xm.mask, ym.mask)
	xm.mask = mask
	ym.mask = mask
	n = np.ma.count(ym, axis=-1)
	a = np.ma.sum(xm * ym, axis=-1) - 1. / n * xm.sum(axis=-1) * ym.sum(axis=-1)
	b = np.ma.sum(xm**2, axis=-1) - 1. / n * xm.sum(axis=-1)**2
	beta = a / b
	xmean = np.ma.mean(xm, axis=-1)
	ymean = np.ma.mean(ym, axis=-1)
	alpha = ymean - beta * xmean
	return beta, alpha

def residual_map(x, y, beta, alpha):
	'''Calculate residual of two arrays wrt linear fit'''
	n = x.shape[-1]
	if y.shape[-1] != n:
		raise ValueError('Inequal input array sizes')
	ycalc = beta[:, :, np.newaxis] * x + alpha[:, :, np.newaxis]
	yres = ycalc - y
	return yres

pr('########################')
pr('# New script execution #')
pr('########################')
pr('# %s, %s' %(_name, _version))
pr('# ' + nowtime())
pr('# Readmode: %s' %rmode)
pr('# Data type: %s' %datatype)

if step in ['medavg']:
	pr('# Creating CDS image files')
	nIDs = len(nIDrange)
	for iID in range(nIDs):
		nID = nIDrange[iID]
		pr('  * nID %i' %nID)
		istart = istartlist[iID]
		for iexp in range(nexps):
			# CDS from single frame cubes
			cdsdata = np.zeros((4096, 4096)).astype('int32')
			file = filebase[0]+'%02i_SINGLE_CUBE_%04i.fits' %(nID, iexp+istart)
			hdulist = fits.open(os.path.join(archivepath, folder, file))
			header = hdulist[0].header
			data = np.rollaxis(hdulist[0].data.astype('int32'), 0, 3)
			cdsdata = data[:, :, 1] - data[:, :, 0]
			# create and save fits file
			cdshdu = fits.PrimaryHDU(cdsdata)
			cdshdu.header = header.copy()
			cdshdu.header['HISTORY'] = 'CDS from single frames'
			filename = filebase[0]+'%02i_CDS_%04i.fits' %(nID, iexp+istart)
			pr('    - Saving output file %s' %filename)
			cdshdulist = fits.HDUList([cdshdu])
			cdshdulist.writeto(os.path.join(inputpath, filename), clobber=True)	
	
	pr('IMPORTANT: Please median average files now in QL!')
	pr('Filenames: %sXX%s.fits' %(filebase[0], filebase[1]))
	raise NotImplementedError('Median averaging has to be done externally')

corrfilename = 'mNONLIN_%s_01.01.fits' %rmode.upper()
hdulist = fits.open(maxsignalfile)
maxsignal = hdulist[0].data

if not step in ['corr', 'plotresid']:
	pr('# Loading image data')
	signals = np.empty((4096, 4096, nIDs))
	itimes = np.zeros(nIDs)
	for iID in range(nIDs):
		nID = nIDrange[iID]
		pr('  * Image number %i' %nID)
		pathlist = os.listdir(inputpath)
		fitsfiles = fnmatch.filter(pathlist, filebase[0]+'%02i%s.fits' %(nID, filebase[1]))
		if len(fitsfiles) == 0:
			raise IOError('No file found for image number %i' %nID)
		if len(fitsfiles) != 1:
			raise IOError('More than one file found for image number %i' %nID)
		# load data
		hdulist = fits.open(os.path.join(inputpath, fitsfiles[0]))
		signals[:, :, iID] = hdulist[0].data
		itimes[iID] = hdulist[0].header['ITIME']

if step in ['calc', 'all']:
	pr('# Caclulating linear corrected data')
	# load correction data
	pr('# Loading correction data')
	linmax, linpoly, nlheader = f_linearity.load_nonlindata(os.path.join(nonlinpath, corrfilename))
	# correct data, create output cube
	linsignals = np.empty((4096, 4096, nIDs))
	for iID in range(nIDs):
		nID = nIDrange[iID]
		pr('  * Processing image number %i' %nID)
		pathlist = os.listdir(inputpath)
		fitsfiles = fnmatch.filter(pathlist, filebase[0]+'%02i%s.fits' %(nID, filebase[1]))
		if len(fitsfiles) == 0:
			raise IOError('No file found for image number %i' %nID)
		if len(fitsfiles) != 1:
			raise IOError('More than one file found for image number %i' %nID)
		datafile = os.path.join(inputpath, fitsfiles[0])
		dataheader = fits.getheader(datafile)
		error = f_linearity.check_nonlin_headers(nlheader, dataheader)
		if error:
			pr('WARNING: Error with data header: %s' %error[1])
		linsignal = f_linearity.correct_nonlin_data(linmax, linpoly, signals[:, :, iID])
		linsignals[:, :, iID] = linsignal
	pr('# Saving corrected data')
	hdu = fits.PrimaryHDU(np.rollaxis(linsignals, 2).astype('float32'))
	filename = 'Lincorrdata_%s_%s' %(datatype, rmode)
	hdulist = fits.HDUList(hdu)
	pr('# Saving data file %s.fits' %filename)
	hdulist.writeto(os.path.join(outputpath, filename+'.fits'), clobber=True)
	
if step in ['plot', 'all']:
	pr('# Plotting random pixel data')
	pr('# Loading corrected data')
	filename = 'Lincorrdata_%s_%s' %(datatype, rmode)
	hdulist = fits.open(os.path.join(outputpath, filename + '.fits'))
	linsignals = np.rollaxis(hdulist[0].data, 0, 3)

	# 10 random pixels per SG
	npx = 10
	np.random.seed(10)
	pxys = np.random.randint(4, 2044, (npx,2))
	SGcorners = [[0, 2048], [2048, 2048], [2048, 0], [0, 0]]
	for iSG in range(4):
		# Plot data
		plt.figure()
		colors = []
		# plot empty lines for colors
		for ipx in range(npx):
			px = SGcorners[iSG][1] + pxys[ipx, 1]
			py = SGcorners[iSG][0] + pxys[ipx, 0]
			dataplt = plt.plot([], [], label='%i, %i'%(px+1, py+1))
			colors.append(dataplt[0].get_color())
		for ipx in range(npx):
			px = SGcorners[iSG][1] + pxys[ipx, 1]
			py = SGcorners[iSG][0] + pxys[ipx, 0]
			signal = signals[py, px, :]
			linsignal = linsignals[py, px, :]
			# plot with offset
			offset = 3000
			plt.plot(0,  ipx * offset, '_', c=colors[ipx], ms=14)
			if np.isnan(linsignal).sum() == nIDs:
				continue
			# line fit
			linpoly = np.ma.polyfit(itimes, np.ma.fix_invalid(linsignal), 1)
			maxtime = np.max(itimes[~np.isnan(linsignal)])
			lintimes = np.linspace(0, maxtime * 1.03, 100)
			plt.plot(itimes, signal + ipx * offset, 'x', c=colors[ipx])
			plt.plot(lintimes, np.polyval(linpoly, lintimes) + ipx * offset, c=colors[ipx])
			plt.plot(itimes, linsignal + ipx * offset, 'o', c=colors[ipx])
		plt.xlim([0, itimes[-1]*1.4])
		plt.ylim(ymin=-5000)
		plt.legend(loc=0, ncol=2)
		plt.grid()
		plt.title('Random pixels with applied nonlinearity correction SG%i' %(iSG+1))
		plt.xlabel('Integration time / s')
		plt.ylabel('Signal (with offset) / ADU')
		plt.figtext(0.02, 0.03, 'x: raw, o: corrected', ha='left', style='italic', size=8)
		plt.figtext(0.02, 0.01, 'line: corrected line fit', ha='left', style='italic', size=8)
		plt.figtext(0.98, 0.03, 'Correction data: %s' %corrfilename, ha='right', style='italic', size=8)
		plt.figtext(0.98, 0.01, 'Data: %s' %datasource, ha='right', style='italic', size=8)
		filename = 'Lincorr_%s_%s_SG%i' %(datatype, rmode, iSG+1)
		plt.savefig(os.path.join(outputpath, filename + '.png'))
		plt.close()
	
# Pearson correlation and histograms over active pixels
if step in ['corr', 'all']:
	pr('# Calculating Pearson correlations')
	pr('# Loading corrected data')
	filename = 'Lincorrdata_%s_%s' %(datatype, rmode)
	hdulist = fits.open(os.path.join(outputpath, filename + '.fits'))
	linsignals = np.rollaxis(hdulist[0].data, 0, 3)
	pr('# Calculating correlation coefficients')
	rcorr = pearsonr_map(itimes, np.ma.fix_invalid(linsignals))
	pr('# Plotting correlation coefficients')
	# Coefficient
	SGcorners = [[0, 2048], [2048, 2048], [2048, 0], [0, 0]]
	fig, axs = plt.subplots(nrows=2, ncols=2)
	plt.figtext(0.02,0.01, 'Non-measurable pixels', ha='left', style='italic', size=8)
	plt.figtext(0.98,0.01, 'Correction data: %s' %corrfilename, ha='right', style='italic', size=8)
	for iSG in range(4):
		ax = axs.flat[iSG]
		SGc = SGcorners[iSG]
		SGa = rcorr[SGc[0]+4:SGc[0]+2044, SGc[1]+4:SGc[1]+2044]
		aflat = SGa[~SGa.mask]
		nnan = SGa.mask.sum()
		amed = np.median(aflat)
		astd = np.std(aflat)
		n, bins, patches = ax.hist(aflat, bins=1000, histtype='step', log=True)
		nmax = np.argmax(n)
		mode = bins[nmax:nmax+2].sum() / 2
		ax.set_xlim([-1.1, 1.1])
		ax.axvline(mode, label='Mode: %6.4f' %mode, color='r')
		ax.text(0.5, 0.93, '%6.4f' %(mode), ha='center', va='center', color='r', transform = ax.transAxes)
		ax.grid()
		ax.set_title('Pearson correlation SG%i' %(iSG+1))
		ax.set_xlabel(r'Correlation coefficient')
		ax.set_ylabel('Number of pixels')
		plt.figtext(0.18+iSG*0.1,0.01, 'SG%i: %i' %(iSG+1, nnan), ha='left', style='italic', size=8)
	plt.tight_layout()
	filename = 'Lincorrcoeff_%s_%s' %(datatype, rmode)
	plt.savefig(os.path.join(outputpath, filename + '.png'))
	plt.savefig(os.path.join(outputpath, filename + '.pdf'))
	plt.close()

# Residual RMS calculation depending on saturation level
if step in ['resid', 'all']:
	pr('# Calculating residuals')
	pr('# Loading corrected data')
	filename = 'Lincorrdata_%s_%s' %(datatype, rmode)
	hdulist = fits.open(os.path.join(outputpath, filename + '.fits'))
	linsignals = np.rollaxis(hdulist[0].data, 0, 3)
	pr('# Calculating linear fits and residuals')
	resrms = np.ma.empty((4096, 4096, nIDs-1))
	satfrac = np.ma.empty((4096, 4096, nIDs-1))
	itimecube = np.ones((4096, 4096, nIDs)) * itimes[np.newaxis, np.newaxis, :]
	
	for ipts in range(nIDs-1):
		pr('  * Points 1-%i' %(nIDs-ipts+1))
		linsignalsm = np.ma.fix_invalid(linsignals)
		for imask in range(1, ipts + 1):
			linsignalsm.mask[:, :, -imask] = True
		beta, alpha = linregression_map(itimecube, linsignalsm)
		ycalc = beta[:, :, np.newaxis] * itimecube + alpha[:, :, np.newaxis]
		yres = ycalc - linsignalsm
		ycalc = 0
		yresrms = yres.std(axis=-1)
		# cut at 3 sigma, fit again
		cutmask = yres > 3 * yresrms[:, :, np.newaxis]
		yres = 0
		newmask = np.ma.mask_or(linsignalsm.mask, cutmask)
		linsignalsm.mask = newmask
		beta, alpha = linregression_map(itimecube, linsignalsm)
		ycalc = beta[:, :, np.newaxis] * itimecube + alpha[:, :, np.newaxis]
		yres = ycalc - linsignalsm
		# relative residual and rms
		yresrel = yres / ycalc
		yres = 0
		ycalc = 0
		yresrelrms = yresrel.std(axis=-1)
		# save as residual rms, get saturation fraction, assume rising values
		resrms[:, :, -ipts-1] = yresrelrms
		satfrac[:, :, -ipts-1] = np.ma.max(np.ma.masked_array(signals, mask=linsignalsm.mask), axis=-1) / maxsignal
		# do not use if last point was masked (duplicates!)
		satfrac.mask[:, :, -ipts-1] = linsignalsm.mask[:, :, -ipts-1]
		linsignalsm = 0
	itimecube = 0
	pr('# Saving residuals and saturation fraction')
	hdu = fits.PrimaryHDU(np.rollaxis(resrms.filled(np.nan), 2).astype('float32'))
	filename = 'Residualrms_%s_%s' %(datatype, rmode)
	hdulist = fits.HDUList(hdu)
	pr('# Saving data file %s.fits' %filename)
	hdulist.writeto(os.path.join(outputpath, filename+'.fits'), clobber=True)
	hdu = fits.PrimaryHDU(np.rollaxis(satfrac.filled(np.nan), 2).astype('float32'))
	filename = 'Satfraction_%s_%s' %(datatype, rmode)
	hdulist = fits.HDUList(hdu)
	pr('# Saving data file %s.fits' %filename)
	hdulist.writeto(os.path.join(outputpath, filename+'.fits'), clobber=True)
	# free memory
	resrms = 0
	satfrac = 0
	
# free memory
signals = 0

# Residual RMS calculation depending on saturation level
if step in ['plotresid', 'all']:
	pr('# Plotting residuals')
	pr('# Loading residual data')
	filename = 'Residualrms_%s_%s' %(datatype, rmode)
	hdulist = fits.open(os.path.join(outputpath, filename + '.fits'))
	resrms = np.ma.fix_invalid(np.rollaxis(hdulist[0].data, 0, 3))
	filename = 'Satfraction_%s_%s' %(datatype, rmode)
	hdulist = fits.open(os.path.join(outputpath, filename + '.fits'))
	satfrac = np.ma.fix_invalid(np.rollaxis(hdulist[0].data, 0, 3))
	pr('# Calculating histograms and averages')
	# mean value at 100 points from histograms
 	nanmask = np.ma.mask_or(resrms.mask, satfrac.mask)
# 	hist1, binedges = np.histogram(satfrac[~nanmask], weights=resrms[~nanmask], bins=100, range=[0,1])
# 	hist2, binedges = np.histogram(satfrac[~nanmask], bins=100, range=[0,1])
# 	meanres = hist1 / hist2
# 	binpts = binedges[0:-1] + np.ediff1d(binedges) / 2

	bins = np.linspace(0, 1, 101)
	binpts = np.linspace(0.5,99.5,100) / 100
	resmean = np.empty(100)
	resstd = np.empty(100)
	resmedian = np.empty(100)
	hist2d = np.empty((100, 200))
	for i in range(99):
		binres = resrms[np.logical_and(satfrac >= bins[i], satfrac <= bins[i+1])]
		resmean[i] = np.ma.mean(binres)
		resmedian[i] = np.ma.median(binres)
		resstd[i] = np.ma.std(binres)
	i = 99
	binres = resrms[np.logical_and(satfrac >= bins[i], satfrac <= bins[i+1])]
	resmean[i] = np.ma.mean(binres)
	resmedian[i] = np.ma.median(binres)
	resstd[i] = np.ma.std(binres)
 	hist2d = np.histogram2d(satfrac[~nanmask], resrms[~nanmask], bins=[100,200], range=[[0, 1], [0, 0.1]])[0]
 	# normalize to peak in each column
 	hist2d /= hist2d.max(axis=1)[:, np.newaxis]
	
	plt.figure()
	plt.axes(axisbg='k')
	plt.imshow(hist2d.transpose(), extent=[0,100,0,10], aspect='auto', origin='lower', interpolation='nearest')
	cbar = plt.colorbar()
	plt.plot(binpts*100, resmedian*100, 'wx', mew=1.5, label='Median')
	plt.ylim(ymax=5)
	leg = plt.legend(loc='upper left', fancybox=True)
	leg.get_frame().set_facecolor('0.3')
	for text in leg.get_texts():
		text.set_color('w')
	plt.grid(color='w')
	plt.title('Residual to line fit after correction')
	plt.xlabel('Saturation fraction / %')
	plt.ylabel('Residual RMS / %')
	cbar.set_label('Normalized number fraction in column')
	plt.figtext(0.98, 0.03, 'Correction data: %s' %corrfilename, ha='right', style='italic', size=8)
	plt.figtext(0.98, 0.01, 'Data: %s' %datasource, ha='right', style='italic', size=8)
	filename = 'Linresidual_%s_%s' %(datatype, rmode)
	plt.savefig(os.path.join(outputpath, filename + '.png'))
	plt.savefig(os.path.join(outputpath, filename + '.pdf'))
	plt.close()
	
	
