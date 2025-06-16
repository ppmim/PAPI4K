---
title: "PAPI: An Open-Source Data Reduction Pipeline for the PANIC Instrument at Calar Alto Observatory"
tags:
  - Python
  - astronomy
  - infrared
  - pipeline

authors:
  - name: Jose Miguel Ibáñez Mengual
    orcid: 0000-0001-6182-0254
    affiliation: 1

affiliations:
  - name: Instituto de Astrofísica de Andalucía (CSIC)
    index: 1

data: 16 Jun 2025
bibliography:
- references.bib
---

# Summary

The PANIC Pipeline (PAPI) is an open-source Python-based software
package designed for the automated reduction of near-infrared imaging
data from the PAnoramic Near-Infrared Camera (PANIC) at the Calar Alto
Observatory (CAHA). Initially developed for the HAWAII-2RG detectors of
PANIC, PAPI has been updated to support the HAWAII-4RG detector
installed in 2025. It provides a comprehensive suite of tools for
processing raw astronomical images, including basic calibration,
cosmic-ray removal, crosstalk correction, sky subtraction, non-linearity
correction, and astrometric calibration. PAPI also includes the PANIC
Quick-Look Tool (PQL), a graphical user interface for prompt data
quality assessment during observations. Available under the GNU General
Public License, PAPI is a versatile tool optimized for broadband imaging
of extragalactic sources, such as galaxy surveys and cluster studies,
and is adaptable to data from other instruments like Omega2000 and
HAWK-I. [@ibanez2010panic]

# Statement of Need

Astronomical data reduction pipelines are critical for processing raw
observational data into science-ready formats. The PANIC instrument, a
near-infrared camera installed at CAHA's 2.2m telescope,
generates complex datasets requiring specialized processing to account
for instrumental effects such as detector non-linearity, crosstalk, and
field distortions. Although there is general purpose astronomical
software, PAPI addresses the specific needs of PANIC data, offering an
automated, user-friendly pipeline that integrates seamlessly with the
observatory's Observing Tool (OT) and GEIRS scripts. Its open-source
nature and Python 3 implementation ensure accessibility, extensibility,
and compatibility with modern astronomical workflows. PAPI fills a gap
for astronomers requiring efficient, high-quality data reduction for
near-infrared imaging, particularly for extragalactic research.

# Functionality 

PAPI automates the reduction of PANIC data through a modular
architecture, with key processing steps including:

- **Basic Calibration**: Removal of instrumental signatures using dark
  and flat-field frames.

- **Cosmic-Ray Removal**: Robust detection and correction of cosmic-ray
  artifacts.

- **Crosstalk Correction**: Mitigation of electronic ghosting in the
  HAWAII-4RG detectors.

- **Sky Subtraction**: Removal of background-sky emission for an
  improved signal-to-noise ratio.

- **Non-Linearity Correction**: Correction of count-rate-dependent
  nonlinearity using polynomial coefficients.

- **Astrometric Registration**: Alignment and mosaicking using
  Astrometry.net and SCAMP for precise World Coordinate System (WCS)
  calibration.

- **Photometric Calibration**: Support for 2MASS-based photometry with
  an accuracy ranging from 0.01 to 0.1 magnitudes, depending on field
  star brightness. [@cardenas2017panic]

The pipeline supports both command-line execution and integration with
PQL, which provides real-time visualization and quality control via a
Qt-based interface. PAPI processes FITS files with 32-bit integer raw
data and outputs 32-bit floating-point reduced images, handling both
single-frame and multi-extension (MEF) formats. Configuration is managed
through a flexible `papi.cfg` file, allowing users to customize
parameters such as input/output directories, calibration settings, and
processing options. [@papi_docs]

# Implementation 

PAPI is implemented in Python 3.7+ and relies on dependencies such as
Astropy, NumPy, and SCAMP, with optional support for Montage and DS9 for
visualization. It is developed and tested on 64-bit Linux systems
(openSUSE 15.4 and Ubuntu 19.1), with installation facilitated through
Anaconda or virtualenv. The pipeline integrates external tools like
SWARP for image co-addition and Astrometry.net for astrometric
calibration, wrapped in Python for seamless operation. The codebase is
hosted on GitHub, with documentation built using Sphinx, available in
HTML and PDF formats. The modular design of PAPI allows for the
standalone execution of individual modules (e.g., to create master
calibration frames) or full pipeline processing via the `run_papi.py`
script. [@papi_docs]

# Usage and Community 

PAPI is primarily designed for PANIC data but is adaptable to other
near-infrared instruments like Omega2000 and HAWK-I, though not fully
optimized for them. It supports both automated reduction of the
observation blocks defined by CAHA's OT and manual processing through
GEIRS scripts. The PQL tool enhances observational efficiency by
enabling real-time monitoring and quality checks, displaying results in
DS9 and matplotlib. The open source license encourages community
contributions, with bug reports and feature requests managed via the
GitHub issue tracker. Recent updates (e.g., version 3.0.0) include
support for the HAWAII-4RG detector and compatibility with modern Linux
distributions. [@papi_docs]

# Citations
- references.bib

# Figures

# Acknowledgements 

We acknowledge support from the Instituto de Astrofísica de Andalucía
(IAA-CSIC) and the Calar Alto Observatory. The development was partially
funded by projects related to the PANIC instrument. The authors thank
the astronomical community for feedback and contributions via GitHub.

# References

[^1]: `jmiguel@iaa.es`
