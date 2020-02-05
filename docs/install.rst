
.. _installation:

Installation & Configuration  
****************************

.. index:: prerequisites, requirements, pipeline


Requirements and Supported Platforms
------------------------------------

System Requirements
+++++++++++++++++++

    * 64-bit Intel/AMD processor (x86_64)
    * 64-bit Linux (glibc ≥ 2.12) or Mac OS X (≥ 10.7)
    * BASH or ZSH as your default shell environment (T/CSH is NOT supported)

Software Requirements
+++++++++++++++++++++

Because PAPI is written mostly in Python_ and ANSI C, it can run on any platform
that has the required Python modules and GCC compilier. However, it has been developed
and deeply tested under `openSuSE`_ 15.1 and `Ubuntu`_ 19.1 x86_64 Linux OS.
`Python 3.6.x <http://www.python.org>`_ or higher and the following packages
are required:

    * `Astropy <http://www.astropy.org/>`_ (4.x)
    * `NumPy <http://numpy.scipy.org/>`_ (> v1.18.x)
    * `SciPy <http://www.scipy.org>`_ (> v1.4.x)
    * `Matplotlib <http://matplotlib.org/>`_ (> v3.1.1)
    * `PyQt5 <http://www.riverbankcomputing.co.uk/software/pyqt/download>`_
    * `IRAF <http://iraf.noao.edu/>`_ with STSDAS and MSCRED (v2.16)
    * `x11iraf <http://iraf.noao.edu/iraf/ftp/iraf/x11iraf/x11iraf-v2.0BETA-bin.linux.tar.gz>`_ for xgterm
    * `PyRAF <http://www.stsci.edu/resources/software_hardware/pyraf/stsci_python>`_ (> v2.14)

The above packages are automatically included in the `Anaconda3`_ package, and then you do not need to install them manually.
However, next tools need to be installed by the user following the instructions included in each package:

    * `CDSClient <http://cdsarc.u-strasbg.fr/doc/cdsclient.html>`_
    * `SExtractor <http://astromatic.iap.fr/software/sextractor/>`_ (> v2.8.6)
    * `SCAMP <http://www.astromatic.net/software/scamp>`_ (> v1.7.0)
    * `SWarp <http://www.astromatic.net/software/swarp>`_ (> v2.19.1)
    * `Astrometry.net <http://astrometry.net/>`_ with `42xx index files <http://broiler.astrometry.net/~dstn/4200/>`_
    * `SAO DS9 and XPA <http://hea-www.harvard.edu/RD/ds9>`_ (> v7.3b5)
    * `Montage <http://montage.ipac.caltech.edu/download/Montage_v3.3.tar.gz>`_ (v3.3)
    * `montage_wrapper <https://pypi.python.org/pypi/montage-wrapper>`_ (0.9.8)
 
Additional packages are optionally required:
    * `sphinx`_  to build the documentation

.. note::
    
    If you are using a SCAMP version <= 2.0.4 (lastest stable version), then you need to install the CDSClient. Otherwise, if you are using SCAMP version > 2.0.4, then you need **libcurl**. 

    Anycase, if you are behind a proxy, you need to set the proxy server in your system::
    
    http_proxy=http//your_proxy:your_port; export http_proxy

    
.. index:: installing, building, source, downloading

Download
--------

The latest stable version of PAPI can be downloaded from `GitHub repository <https://github.com/ppmim/PAPI>`_ .

Environment Installation
------------------------
The PAPI package can be installed into a virtualenv or `Conda`_ (prefered) environment
manager via pip. We recommend a fresh environment with only python installed. Via Conda:

1. Install `Anaconda3`_ (for Python 3.7), which include Conda manager::

    $ sh Anaconda3-2019.10-Linux-x86_64.sh


2. Create environment (papienv) and install PyRAF::

    $ conda create -n papienv python=3.7
    $ conda config --add channels http://ssb.stsci.edu/astroconda
    $ conda install python=3.7 iraf-all pyraf-all

.. warning::

    Due to Python 3.x incompatibilities present in several tasks, `STScI`_ recommends to install IRAF alongside Python 2.7.
    However, PAPI is implemented for Python3, and no problems was found by the moment.


After the installation is complete go ahead and activate the “papienv” environment.
This command only needs to be executed one time per terminal session::

    $ conda activate  papienv

3. Install other Python staff::

    $ conda install -c astropy ccdproc==2
    $ pip install montage_wrapper
    $ pip install sphinx_rtd_theme

4. Install Third Party tools:

First we need to install next modules required for those third party tools::

    $ sudo zypper install libXmu6-32bit libncurses5-32bit
    (for IRAF 32-bit compatibility)
    $ sudo zypper install libXt-devel libnsl-devel cfitsio-devel
    $ sudo zypper install python2-devel
    (required for astrometry.net)


 Montage
 '''''''

    $ mkdir /home/panic/Software/PAPI/; cd /home/panic/Software/PAPI/
    $ wget https://irsa.ipac.caltech.edu/Montage/download/Montage_v3.3.tar.gz
    $ tar -xvzf Montage_v3.3.tar.gz
    $ cd Montage_v3.3
    $ make
    $ export PATH=$PATH:/home/panic/Software/PAPI/Montage_v3.3/bin

 DS9
 '''

    $ wget http://ds9.si.edu/download/opensuse15/ds9.opensuse15.8.1.tar.gz
    $ tar -xvzf ds9.opensuse15.8.1.tar.gz
    $ cp ds9 /usr/local/bin/

  XPA
  '''

    $ git clone https://github.com/ericmandel/xpa.git
    $ ./configure
    $ make install

  Astrometry.net
  ''''''''''''''

    $ wget http://astrometry.net/downloads/astrometry.net-latest.tar.gz
    $ tar -xvzf
    $ cd astrometry.net
    $ make install
    $ export PATH=$PATH:/usr/local/astrometry/bin/

And then download and copy the 42xx index files from::

   wget http://broiler.astrometry.net/~dstn/4200/

to::

    /usr/local/astrometry/data

And then update and config file::

   /usr/local/astrometry/etc/astrometry.cfg


  Astromatic.net
  ''''''''''''''

    $ sudo zypper install fftw3-devel
    $ sudo zypper install libplplot16
    $ sudo zypper install cblas-devel

    $ rpm -i swarp-2.38.0-1.x86_64.rpm
    $ rpm -i sextractor-2.19.5-1.x86_64.rpm
    $ rpm -i --nodpes scamp-2.0.4-1.x86_64.rpm

    $ sudo ln -s /usr/lib64/libqhull.so.7 /usr/lib64/libqhull.so.5
    $ sudo ln -s /usr/lib64/libplplot.so.16 /usr/lib64/libplplotd.so.11

PAPI Installation
-----------------

To install a released (tagged) version, you can install directly from Github.  To install tagged release ``papi 2.1.0``::

    $ pip install git+https://github.com/ppmim/PAPI.git@2.1.0

The latest development version (from ``master``) can also be installed from Github::

    $ pip install git+https://github.com/ppmim/PAPI.git

As can a particular commit hash::

    $ pip install git+https://github.com/ppmim/PAPI.git@3f03323c




Installing for developers
-------------------------

Fork and clone the repo::

    $ git clone https://github.com/ppmim/PAPI.git
    $ cd PAPI

Install from your local checked out copy as an "editable" install::

    $ pip install -e .

If you want to run the tests and/or build the docs, you can make sure those dependencies are installed too::

    $ pip install -e .[test]
    $ pip install -e .[docs]
    $ pip install -e .[test,docs]

Note: If you wish to install directly from github, but also include the extra dependencies, the syntax is as follows::

    $ pip install "papi[test] @ git+https://github.com/ppmim/PAPI.git"

Need other useful packages in your development environment::

    $ pip install ipython flake8 pytest-xdist


Edit the papi_setup.sh and set the right values to PAPI_CONFIG, and then run the script as an user::

    $ ./papi_setup.sh

.. warning::
    
    The script papi_setup.sh is currently implemented **only** for the Bash shell, and will modify your .bashrc file adding a new line at the end.

    

Building the documentation
--------------------------

The PAPI documentation is base on `sphinx`_. With the package installed, the 
html documentation can be built from the `doc` directory::

  $ cd papi/doc
  $ make html
  
The documentation will be copied to a directory under `build/sphinx`.
  
The documentation can be built in different formats. The complete list will appear
if you type `make`.

Bug reports
-----------

Please submit issues with the `issue tracker`_ on github.


Release Notes
-------------
* 2.0.x
    - Support for new PANIC detector H4RG
    - Support for Python 3.7.x and Conda environment

* 1.2.x
    - Support for new MEF structure (Qi); old format (SGi_1) also supported
    - Bug Fixes
* 1.0.x
    - First version
    
    
.. _PANIC: http://www.iaa.es/PANIC
.. _CAHA: http://www.caha.es
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
