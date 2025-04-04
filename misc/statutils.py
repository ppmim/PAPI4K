"""
Statistics procedures.
"""

import numpy
import scipy.stats


def mad(data, sigma=True):
    """
    Return the median absolute deviation.
    """
    med = numpy.median(data)
    mad = numpy.median(numpy.abs(data - med))
    if sigma == False:
        return mad
    else:
        return mad*1.4826

def sigma_rob(data, iterations=1, thresh=3.0):
    """
    Iterative m.a.d. based sigma with positive outlier rejection.
    """
    noise = mad(data)
    for i in range(iterations):
        ind = (data <= thresh * noise).nonzero()
        noise = mad(data[ind])
    return noise

def sig_n_outliers(n_data, n_out=1.0, pos_only=True):
    """
    Return the sigma needed to expect n (default 1) outliers given
    n_data points.
    """
    perc = float(n_out) / float(n_data)
    if not pos_only:
        perc *= 2.0
    return abs(scipy.stats.norm.ppf(perc))


def MAD(a, c=0.6745, axis=0):
    """
    Median Absolute Deviation along given axis of an array:

    median(abs(a - median(a))) / c

    c = 0.6745 is the constant to convert from MAD to std; it is used by
    default
    
    Parameters
    ----------
    
    a : array 
        data array
    c : float
        coeff to convert from MAD to std; 0.6745 default 
    axis : int
        axis direction in which to compute
    
    """

    good = (a == a)
    a = numpy.asarray(a, numpy.float64)
    if a.ndim == 1:
        d = numpy.median(a[good])
        m = numpy.median(numpy.fabs(a[good] - d) / c)
    else:
        d = numpy.median(a[good], axis=axis)
        # I don't want the array to change so I have to copy it?
        if axis > 0:
            aswp = numpy.swapaxes(a[good], 0, axis)
        else:
            aswp = a[good]
        m = numpy.median(numpy.fabs(aswp - d) / c, axis=0)

    return m

def nanmedian(arr):
    """
    Returns median ignoring NAN values
    """
    return numpy.median(arr[arr == arr])

def nan2num(a, replace=0):
    """ Replace `nan` or `inf` entries with the `replace` keyword
    value.

    If replace is "mean", use the mean of the array to replace
    values. If it's "interp", intepolate from the nearest values.
    """
    a = numpy.atleast_1d(a)
    b = numpy.array(a, copy=True)
    bad = numpy.isnan(b) | numpy.isinf(b)
    if replace == 'mean' and (~bad).sum() > 0:
        replace = b[~bad].mean().astype(b.dtype)
    elif replace == 'interp':
        x = numpy.arange(len(a))
        replace = numpy.interp(x[bad], x[~bad], b[~bad]).astype(b.dtype)
        
    b[bad] = replace
    if len(b) == 1:
        return b[0]
    return b
