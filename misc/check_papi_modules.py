#!/usr/bin/env python

__doc__ = """
Check the existence of necessary Python modules for PAPI
"""

import sys
import string
from distutils import spawn

bold = "\033[1m"         # print bold
probbold = "\033[1;31m"  # print bold red 
reset = "\033[0;0m"      # reset special print settings


def testmodule(modulename, moduleversion):
    """
    test if a Python module is installed, and
    if yes, if its version is equal or higher than
    a reference version
    """

    print(bold +
          "Testing Python module installation for module '%s':" %
          (modulename) + reset)
    print("PAPI needs at least version %s" % (moduleversion))
    
    try:
        mod = __import__(modulename)
        refversion = moduleversion.split(".")
        if modulename == "PyQt5.QtCore":
            cv = mod.QtCore.PYQT_VERSION_STR
            currversion = cv.split(".")
            currversion = [ a.split('-')[0] for a in currversion ]
        else:
            cv = mod.__version__
            currversion = cv.split(".")
            currversion = [ a.split('-')[0] for a in currversion ]

        if list(map(int, currversion)) < list(map(int, refversion)):
            print(probbold + "PROBLEM: You have it with V%s\n" %
                  (cv) + reset)
        else:
            print("Your version %s of '%s' is fine!\n" %
                  (cv, modulename))
    except Exception as ex:
        print(probbold)
        print(probbold +
              "PROBLEM: You do not have the Python module '%s' installed! (%s)\n" %
              (modulename, ex) + reset)


def check_modules():
    # --------------------
    # Check Python version
    # --------------------
    print(bold + "PAPI Python checking tool" + reset)
    print(bold + "=========================" + reset)
    print("\n")
    print(bold + "Checking Python Version:" + reset)
    print("PAPI needs Python Version 3.Y with Y>=6")
    pyversion = sys.version.split()[0].split('.')[:2]

    if list(map(int, pyversion)) > [3, 7] or list(map(int, pyversion)) < [3, 2]:
        print(probbold + "PROBLEM: You have Python V%s.%s\n"
                          % (pyversion[0], pyversion[1]) + reset)
        print("\n")
    else:
        print("Your Python version %s is fine!" % pyversion)
        print("\n")
    
    # ----------------------------------------------------
    # Define the Python modules, and the versions we need
    # ----------------------------------------------------
    PAPImodules = { 'numpy': '1.20', 'pyraf' : '2.1',
                   'matplotlib' : '3.5.0', 'scipy': '1.7', 
                   'PyQt5.QtCore': '5.8',
                   'astropy': '4.3', 'montage_wrapper': '0.9.8' }
    
    # -----------------
    # Check the modules
    # -----------------
    for modulename in PAPImodules.keys():
        testmodule(modulename, PAPImodules[modulename])


def check_install():
    """
    Check PAPI installation (external tools as Astrometry.net, SExtractor, SCAMP,...)
    """
    
    print(bold + "PAPI checking external tools" + reset)
    print(bold + "============================" + reset)
    print("\n")
    # Check external tools (Astromatic.net, IRAF, xgterm, Astrometry.net, ...)
    astromatic = ['sex', 'scamp', 'swarp','aclient',
                  'cl','mkiraf','xgterm',
                  'solve-field',
                  'ds9', 'xpaaccess',
                  'mAdd','mProjExec','mProject',
                  'skyfilter']
    for tool in astromatic:
        if not spawn.find_executable(tool):
            print(probbold + "Tool %s was not found in your path" % tool + reset)
        else:
            # check libs dependencies (eg., libplplot) 
            tool_path = spawn.find_executable(tool)
            # TBD
            print(tool_path)
       
    
    
################################################################################
# main
if __name__ == "__main__":
    check_modules()
    check_install()
    sys.exit(0)
    
