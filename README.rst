|logo| PAPI
===========

PAPI (PANIC Pipeline) is the automatic image processing pipeline for data obtained 
with the PAnoramic Near Infrared Camera (PANIC_) for the 2.2m and 3.5m Telescopes at 
Calar Alto Observatory (CAHA_). The pipeline is written in Python and developed 
at the `Institute of Astrophysics of Andalusia (CSIC) <http://www.iaa.es/>`_. 
The automated processing steps include basic calibration (removeing instrumental 
signature), cosmic-ray removal, treatment for electronic ghosts (cross-talk), 
sky subtraction, non-linear count-rate correction, robust alignment and 
registration.

Although PAPI was developed for the PANIC camera with H2RG detector, it was updated 
in 2022 to support the new H4RG detector integrated into PANIC. 

PANIC_ is a general purpose Panoramic Near Infrared camera for Calar Alto. 
It is optimized for use at the 2.2m telescope, but can also be installed 
at the 3.5m telescope. It works in the nIR bands Z, J, H and K. 



Installation
============

PAPI has the following strict requirements:
 
 - `Python`_ 3.7
 - Numpy 1.18.x or later
 - `Anaconda`_ 2022.05-2024.10
 - `IRAF`_ 2.16

and also depends on next packages:

 * `NumPy <http://numpy.scipy.org/>`_ (> v1.18.x)
    * `SciPy <http://www.scipy.org>`_ (> v1.4.x)
    * `Astropy <http://www.astropy.org/>`_ (4.3.1)
    * `Matplotlib <http://matplotlib.org/>`_ (> v3.1.1)
    * `PyQt5 <http://www.riverbankcomputing.co.uk/software/pyqt/download>`_
    * `IRAF <http://iraf.noao.edu/>`_ with STSDAS and MSCRED (v2.16)
    * `x11iraf <http://iraf.noao.edu/iraf/ftp/iraf/x11iraf/x11iraf-v2.0BETA-bin.linux.tar.gz>`_ for xgterm
    * `PyRAF <http://www.stsci.edu/resources/software_hardware/pyraf/stsci_python>`_ (> v2.14)

The above packages are automatically included in the `Anaconda` package, and then you do not need to install them manually.
However, next tools need to be installed by the user following the instructions included in each package:

    * `CDSClient <http://cdsarc.u-strasbg.fr/doc/cdsclient.html>`_
    * `SExtractor <http://astromatic.iap.fr/software/sextractor/>`_ (> v2.25)
    * `SCAMP <http://www.astromatic.net/software/scamp>`_ (> v2.10)
    * `SWarp <http://www.astromatic.net/software/swarp>`_ (> v2.41.5)
    * `Astrometry.net <http://astrometry.net/>`_ with `42xx index files <http://broiler.astrometry.net/~dstn/4200/>`_
    * `SAO DS9 and XPA <http://hea-www.harvard.edu/RD/ds9>`_ (v8.5)
    * `Montage <http://montage.ipac.caltech.edu/download/Montage_v3.3.tar.gz>`_ (v3.3)
    * `montage_wrapper <https://pypi.python.org/pypi/montage-wrapper>`_ (0.9.8)

Note that, for PyRAF_ you have to install IRAF_ (v2.16 or later), what can be a 
tricky task. However, is has been simplified in recent versions.

Installation steps
------------------
The PAPI package can be installed into a virtualenv or `Conda`_ (prefered) environment
manager via pip. We recommend a fresh environment with only python installed. Via Conda:

1. Install `Anaconda3`_ (for Python 3.7), which include Conda manager.

2. Create environment (papienv) and install PyRAF::

    $ conda config --add channels http://ssb.stsci.edu/astroconda
    $ conda create -n papienv python=3.7 iraf-all pyraf-all

.. warning::

    Due to Python 3.x incompatibilities present in several tasks, `STScI`_ recommends to install IRAF alongside Python 2.7.
    However, PAPI is implemented for Python3, and no problems was found by the moment.


After the installation is complete go ahead and activate the “papienv” environment.
This command only needs to be executed one time per terminal session::

    $ conda activate  papienv

3. Install the tools required by PAPI (TBC, requirements.txt ?)::

    $ pip install scipy
    $ pip install montage_wrapper
    $ conda install -c astropy ccdproc==2

Installing for end-users
++++++++++++++++++++++++

To install a released (tagged) version, you can install directly from Github.  To install tagged release ``papi 2.1.0``::

    $ pip install git+https://github.com/ppmim/PAPI.git@2.1.0

The latest development version (from ``master``) can also be installed from Github::

    $ pip install git+https://github.com/ppmim/PAPI.git

As can a particular commit hash::

    $ pip install git+https://github.com/ppmim/PAPI.git@3f03323c


.. warning::
    
    The script papi_setup.sh is currently implemented **only** for the Bash shell, and will modify your .bashrc file adding a new line at the end.


#. Go to config_files/ directory to setup the config file to use.

.. note::
    
    If you are behind a proxy, you need to set the proxy in your system::
    
    http_proxy=http//your_proxy:your_port; export http_proxy 


Supported Platforms
===================
Currently PAPI has only be tested under openSuSE15.5 and Ubuntu 24.04, but it
should work on any 64-bit Linux box with the software packages required above.


Documentation
=============
You can browse the latest release documentation_ online.



Webpage: http://www.iaa.es/PANIC
Maintainer: jmiguel@iaa.es


.. links:
.. |logo| image:: ./papi/QL/resources/logo_PANIC_100.jpg
          :width: 127 px
          :alt: PANIC icon

.. _PANIC: http://www.iaa.es/PANIC
.. _CAHA: http://www.caha.es
.. _iaa_web: http://www.iaa.es
.. _mpia_web: http://www.mpia.de
.. _source code: http://github.com/ppmim/PAPI
.. _documentation: http://www.iaa.es/~jmiguel/PANIC/PAPI/html/index.html
.. _SciPy: http://www.scipy.org
.. _PyFITS: http://www.stsci.edu/resources/software_hardware/pyfits
.. _PyRAF: http://www.stsci.edu/institute/software_hardware/pyraf
.. _PyQt5: http://www.riverbankcomputing.co.uk/software/pyqt/download
.. _Astropy: http://www.astropy.org/
.. _Astrometry.net: http://astrometry.net/
.. _Astromatic: http://www.astromatic.net/
.. _Sphinx: http://sphinx-doc.org/
.. _IRAF: http://www.iraf.net
.. _Omega2000: http://www.caha.es/CAHA/Instruments/O2000/index.html
.. _HAWK-I: http://www.eso.org/sci/facilities/paranal/instruments/hawki/
.. _sphinx: https://pypi.org/project/Sphinx/
.. _pdf: http://www.iaa.es/~jmiguel/PANIC/PAPI/PAPI.pdf
.. _openSuSE: http://www.opensuse.org/
.. _Ubuntu: https://ubuntu.com/download/desktop
.. _Conda: https://docs.conda.io/projects/conda/en/latest/index.html
.. _Anaconda3: https://www.anaconda.com/distribution/#download-section
.. _issue tracker: https://github.com/ppmim/PAPI/issues
.. _Python: http://www.python.org
.. _STScI: https://astroconda.readthedocs.io/en/latest/installation.html
