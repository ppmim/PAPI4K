#!/usr/bin/env python
#########################################################################
# PANIC hardware logging
# Log instrument mounting cycles, create FITS header entries, copy log
# file to other panic computer
# 
# This script provides an easy way to add telescope mounting cycles in the
# hardware log file. It also has functions to create the corresponding FITS
# header entries for GEIRS, and copy the log file to the other panic
# computer. For more details, consult the documentation in PANIC-SW-SP-01.
#
# usage: log_mountcycle.py [-h] [-f | -c] [--logpath LOGPATH]
#                          [--logfile LOGFILE] [--fitspath FITSPATH]
#                          [--fitsfile FITSFILE] [--targetuser TARGETUSER]
#                          [--targethost TARGETHOST]
# 
# Script to edit the PANIC telescope mounting cycle log, create the corresonding
# FITS header keyword inputs for GEIRS, and copy the log file to the other panic
# computer
# 
# optional arguments:
#   -h, --help            show this help message and exit
#   -f, --fitsonly        Only write FITS header file data, silent mode
#   -c, --copyonly        Only copy log file to other panic computer
#   --logpath LOGPATH     Logfile path, default: '/data1/PANIC/HWlogs'
#   --logfile LOGFILE     Logfile filename, default: log_mounting22/35.txt
#                         (depending on $TELESCOPE or computer name)
#   --fitspath FITSPATH   FITS header input path, default: $TMPDIR or ~/tmp
#   --fitsfile FITSFILE   FITS header input filename, default:
#                         geirsPhduAdd.panic_3
#   --targetuser TARGETUSER
#                         User account on second panic computer to copy logfile,
#                         default: Determine from local host name
#   --targethost TARGETHOST
#                         Name of second panic computer to copy logfile,
#                         default: Determine from local host name
# 
# 1.0 31/03/2015 BD Creation
# 1.1 01/04/2015 BD Update
#	1) Added fitsonly flag for silent generation of FITS header file
#	2) Added internal verbose flag
#	3) Added verification of log data when loading
#	4) Measuring time in UTC
#	5) Removed unnecessary main while loop
#	6) Added check of number of entries when loading logfile
#	7) Changed print of log entries to 5 or maximum available lines
#	8) New cycle with maximum number + 1
#	9) Clarified manual time edit
#	10) Added selection of logfile name depending on telescope setting or
#	computer name
# 1.1.1 01/04/2015 BD Update
#	1) Clarified manual date edit
#	2) Fixed --fitsonly help text
# 1.2 15/04/2015 BD Update
#	1) Added copying logfile to other panic computer
# 1.3 28/11/2022 JMIM Update: for PANICv2
# 
# $Id:$
_name = 'log_mountcycle.py'
_version = '1.3'
#########################################################################
import os
import argparse
import datetime
import socket
import subprocess

# parse command line arguments
parser = argparse.ArgumentParser(description='Script to edit the PANIC telescope mounting cycle log, create the corresonding FITS header keyword inputs for GEIRS, and copy the log file to the other panic computer')
arggroup = parser.add_mutually_exclusive_group()
arggroup.add_argument('-f', '--fitsonly', help='Only write FITS header file data, silent mode', action='store_true')
arggroup.add_argument('-c', '--copyonly', help='Only copy log file to other panic computer', action='store_true')
parser.add_argument('--logpath', help="Logfile path, default: '/data1/PANIC/HWlogs'", type=str, default='/data1/PANIC/HWlogs')
parser.add_argument('--logfile', help="Logfile filename, default: log_mounting22/35.txt (depending on $TELESCOPE or computer name)", type=str)
parser.add_argument('--fitspath', help="FITS header input path, default: $TMPDIR or ~/tmp", type=str)
parser.add_argument('--fitsfile', help="FITS header input filename, default: geirsPhduAdd.panic_3", type=str, default='geirsPhduAdd.panic_3')
parser.add_argument('--targetuser', help="User account on second panic computer to copy logfile, default: Determine from local host name", type=str)
parser.add_argument('--targethost', help="Name of second panic computer to copy logfile, default: Determine from local host name", type=str)
args = parser.parse_args()
args = parser.parse_args()
fitsonly = args.fitsonly
copyonly = args.copyonly
logpath = args.logpath
logfilename = args.logfile
fitspath = args.fitspath
FITSfilename = args.fitsfile
targetuser = args.targetuser
targethost = args.targethost
if fitsonly:
	verbose = 0
else:
	verbose = 1

if not logfilename:
	# Logfile name: test for telescope variable, or computer name
	telescope = os.environ.get('TELESCOPE')
	if telescope == 'CA2.2m':
		logfilename = 'log_mounting22.txt'
	elif telescope == 'CA3.5m':
		logfilename = 'log_mounting35.txt'
	else:
		hostname = socket.gethostname()
		if hostname == 'panic22':
			logfilename = 'log_mounting22.txt'
		elif hostname == 'panic35':
			logfilename = 'log_mounting35.txt'
		else:
			raise IOError('Cannot determine telescope, please specify log filename in input')
logfilepath = os.path.join(logpath, logfilename)
if not fitspath:
	# FITS header file path: either $TMPDIR or ~/tmp
	FITSpath = os.environ.get('TMPDIR', os.path.join(os.path.expanduser('~'), 'tmp'))
else:
	FITSpath = fitspath
FITSfilepath = os.path.join(FITSpath, FITSfilename)

def nowtime():
	return datetime.datetime.utcnow()

def loadlogfiledata(logfilepath):
	'''Load data of log file
	Input
	-----
	logfilepath : str
			  Fully qualified path of logfile
	Returns
	-------
	nrs, dates, times, comments : lists
				Number, date, time, and comment lists of file data (int, str, str, str)
	'''
	if not os.path.exists(logfilepath):
		raise IOError('Mounting log file {} not found!'.format(logfilepath))
	else:
		nrs = []
		dates = []
		times = []
		comments = []
		logfile = open(logfilepath, 'r')
		lines = logfile.readlines()
		for line in lines:
			tokens = line.split(';')
			if tokens[0].strip()[0] == '#':
				continue
			nr = tokens[0].strip()
			try:
				int(nr)
			except ValueError:
				raise ValueError('Invalid number entry "{}" in mounting log, type must be integer'.format(nr))
			nrs.append(int(nr))
			date = tokens[1].strip()
			try:
				datetime.datetime.strptime(date, '%Y-%m-%d')
			except ValueError:
				raise ValueError('Invalid date entry "{}" in mounting log, format must be YYYY-mm-dd'.format(date))
			dates.append(date)
			time = tokens[2].strip()
			try:
				datetime.datetime.strptime(time, '%H:%M')
			except ValueError:
				raise ValueError('Invalid time entry "{}" in mounting log, format must be HH:MM'.format(time))
			times.append(time)
			comments.append(tokens[3].strip())
		logfile.close()
		if len(nrs) == 0:
			raise IOError('No valid entries found in mounting log file {}'.format(logfilepath))
		return nrs, dates, times, comments

if verbose:
	print('# New execution of {}, {}'.format(_name, _version))
	print('# ' + nowtime().isoformat())

	# load data from text files
	print('# Loading telescope mounting logfile data')
nrs, dates, times, comments = loadlogfiledata(logfilepath)
if verbose:
	nlines = min(len(nrs), 5)
	print('# Last {} log entries:'.format(nlines))
	print(' Nr Date       UTC   Comment')
	for i in range(nlines, 0, -1):
		print('{:3} {} {} {}'.format(nrs[-i], dates[-i], times[-i], comments[-i]))

if not fitsonly and not copyonly:
	print('Do you want to:')
	print('(A) Add new cycle and create FITS header data')
	print('(F) Create FITS header data from last entry')
	print('(C) Only copy log file to other panic computer')
	print('(X) Exit')
	while True:
		# verify input
		action = input().upper()
		if action not in ['A', 'F', 'X', 'C']:
			print('Error: Wrong input, try again')
		else:
			break
elif fitsonly:
	action = 'F'
elif copyonly:
	action = 'C'
	
if action == 'X':
	pass

if action == 'A':
	# Add new log entry
	print('# Adding new cycle in logfile')
	# number: increase maximum one
	nr = max(nrs) + 1
	# date and time
	print('Enter cycle starting point: (N) Now or (M) Manually:')
	while True:
		# verify input
		ans = input().upper()
		if ans not in ['N', 'M']:
			print('Error: Wrong input, try again')
		else:
			break
	if ans.upper() == 'N':
		start = nowtime()
		date = start.date().isoformat()
		time = start.time().isoformat()[:5]
	else:
		# manual entry of date and time, check validity
		print('Enter cycle start date in UT YYYY-mm-dd:')
		while True:
			ans = input()
			try:
				datetime.datetime.strptime(ans, '%Y-%m-%d')
			except ValueError:
				print('Error: wrong input, format must be YYYY-mm-dd, try again')
			else:
				break
		date = ans
		print('Enter cycle start time in UT HH:MM:')
		while True:
			ans = input()
			try:
				datetime.datetime.strptime(ans, '%H:%M')
			except ValueError:
				print('Error: wrong input, format must be HH:MM, try again')
			else:
				break
		time = ans
	# comment
	print('Enter comment (no ";" allowed):')
	while True:
		ans = input()
		if ';' in ans:
			print('Error: wrong input, no ";" allowed, try again')
		else:
			break
	comment = ans
	# add line to logfile
	logfile = open(logfilepath, 'a')
	logfile.write('{}; {}; {}; {}\n'.format(nr, date, time, comment))
	logfile.close()		
	print('# New cycle added to logfile')

if action in ['F', 'A']:
	# Write last entry to FITS header input file
	# Get last entry if not added before
	if action == 'F':
		nr = nrs[-1]
		date = dates[-1]
		time = times[-1]
		comment = comments[-1]
	# convert date and time to ISO format
	cycldate = datetime.datetime.combine(datetime.datetime.strptime(date, '%Y-%m-%d').date(), datetime.datetime.strptime(time, '%H:%M').time())
	isodate = cycldate.isoformat()
	# lines for files
	cyclkey = "MNTCYCL = {} / {}\n".format(nr, 'Mounting cycle number')
	datekey = "MNTDATE = '{}' / {}\n".format(isodate, 'UT-date of mounting cycle start')
	if os.path.exists(FITSfilepath):
		# load file if existing
		if verbose:
			print('# Loading existing FITS header input')
		headerfile = open(FITSfilepath, 'r')
		lines = headerfile.readlines()
		headerfile.close()
		newlines = []
		cyclwritten = False
		datewritten = False
		for line in lines:
			# find relevant keywords and replace lines
			if line.strip().startswith('MNTCYCL'):
				line = cyclkey
				cyclwritten = True
			if line.strip().startswith('MNTDATE'):
				line = datekey
				datewritten = True
			newlines.append(line)
		# none of the lines contain the keys:
		if not cyclwritten:
			newlines.append(cyclkey)
		if not datewritten:
			newlines.append(datekey)
		# write file again
		headerfile = open(FITSfilepath, 'w')
		headerfile.writelines(newlines)
		headerfile.close()
		if verbose:
			print('# FITS header input file updated')
	else:
		# Create new file
		headerfile = open(FITSfilepath, 'w')
		headerfile.write('# FITS header keywords for PANIC cycles, do not delete!\n')
		headerfile.write(cyclkey)
		headerfile.write(datekey)
		headerfile.close()
		if verbose:
			print('# FITS header input file written')

if action in ['A', 'C']:
	# copy log file to other panic computer for backup reasons
	# determine current one, if necessary derive names on target computer
	# errors here prevent the backup on the other computer, but do not
	# impact the general script purpose, so don't raise errors
	hostname = socket.gethostname()
	while True:
		if not targethost:
			if hostname == 'panic22':
				targethost = 'panic35'
			elif hostname == 'panic35':
				targethost = 'panic22'
			else:
				print('Error: Unknow local host name (not "panic22" or "panic35"), cannot determine target host name, please specify in input')
				print('WARNING: Log file could not be backed up on onther panic computer!')
				break
		if not targetuser:
			if hostname == 'panic22':
				targetuser = 'obs35'
			elif hostname == 'panic35':
				targetuser = 'obs22'
			else:
				print('Error: Unknow local host name (not "panic22" or "panic35"), cannot determine target user name, please specify in input')
				print('WARNING: Log file could not be backed up on onther panic computer!')
				break
		# copy file, check for errors
		targetpath = '{}@{}:/data1/PANIC/HWlogs'.format(targetuser, targethost)
		print('# Copying {} to {}'.format(logfilepath, targetpath))
		error = subprocess.call(['rcp', '-p', '{}'.format(logfilepath), targetpath])
		if error != 0:
			print('Error: Copying log file to {} failed!'.format(targethost))
			print('WARNING: Log file could not be backed up on onther panic computer!')
			break
		else:
			print('# Log file copied to {}'.format(targethost))
			break
	
if verbose:
	print('# Script terminated')
