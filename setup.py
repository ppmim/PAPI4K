from os.path import basename
from setuptools import setup, find_packages
from glob import glob
from buildqt import BuildQt
from setuptools.command.install import install
import os
import subprocess


class InstallWrapper(install):
    """
    This class provide a wrapper around the install procedure to run some
    specific task for PAPI installation:
    1) IRDR compilation

    """
    def finalize_options(self):
        install.finalize_options(self)
        self.install_lib = self.install_platlib

    def run(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        print("[InstallWrapper] Dir = %s" % dir_path)
        try:
            irdr_directory = os.path.join(dir_path, 'papi/irdr')
            print(irdr_directory)
            if not os.path.exists(irdr_directory):
                return
            os.chdir(irdr_directory)
            subprocess.run(['make', 'all'])
            os.chdir("../..")
        except Exception as e:
            print(str(e))
            raise e

        print("Now, run standard install...")
        try:
            self.run_command("build")
            # install.run(self)
            install.do_egg_install(self)
        except Exception as e:
            print(str(e))


NAME = 'papi'
irdr_bins = [s for s in glob('papi/irdr/bin/*')]
SCRIPTS = [s for s in glob('scripts/*') if basename(s) != '__pycache__']

PACKAGE_DATA = {
    '': [
        '*.fits',
        '*.txt',
        '*.inc',
        '*.cfg',
        '*.csv',
        '*.yaml',
        '*.json',
        '*.asdf',
        '*.ui',
        'papi/QL/resources/*',
    ]
}
DOCS_REQUIRE = [
    'matplotlib',
    'sphinx',
    'sphinx-automodapi',
    'sphinx-rtd-theme',
    'sphinx-astropy',
    'sphinx-asdf',
]
TESTS_REQUIRE = [
    'pytest',
    'pytest-doctestplus',
    'requests_mock',
    'pytest-openfiles',
    'pytest-cov',
    'codecov',
]

cmdclass = {}
cmdclass['build_qt'] = BuildQt
cmdclass['install'] = InstallWrapper

setup(
    name=NAME,
    version="2.0",
    use_scm_version={"root": "."},
    author='Jose-Miguel Ibanez-Mengual IAA-CSIC',
    description='The data processing pipeline for the PANIC instrument',
    long_description=('PAPI is the automatic data processing software for the PANIC'
                      'instrument, the PAnoramic Near Infrared Camera for CAHA Observatory.'
                      ' The automated processing steps include basic calibration '
                      '(removeing instrumental signature), cosmic-ray removal, treatment'
                      ' for electronic ghosts (cross-talk), sky subtraction, non-linear '
                      'count-rate correction, robust alignment and registration.'
                      ),
    url='https://github.com/ppmim/PAPI',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GPL License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: C',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    include_package_data=True,
    python_requires='>=3.7',
    scripts=SCRIPTS,
    packages=find_packages(exclude=["tmp", "docs", "Others*"]),
    package_data=PACKAGE_DATA,
    exclude_package_data={"Others": ['*'], "docs": ["*"]},
    setup_requires=[
        'setuptools_scm',
    ],
    install_requires=[
        'astropy>=4.0, <5',
        'pyds9>=1.8.1',
    ],
    extras_require={
        'docs': DOCS_REQUIRE,
        'test': TESTS_REQUIRE,
    },
    tests_require=TESTS_REQUIRE,
    entry_points={
        'console_scripts': ['papi=papi.papi:main', 'papi_ql=papi.QL.runQL:main',
                            'mef=papi.misc.mef:main',
                            'calDark=papi.reduce.calDark:main',
                            'calDarkModel=papi.reduce.calDarkmodel:main',
                            'astrowarp=papi.reduce.astrowarp:main',
                            'applyDarkFlat=papi.reduce.applyDarkFlat:main',
                            'solveAstrometry=papi.reduce.solveAstrometry:main',
                            'calBPM=papi.reduce.calBPM:main',
                            'calDomeFlat=papi.reduce.calDomeFlat:main',
                            'calSuperFlat=papi.reduce.calSuperFlat:main',
                            'calTwFlat=papi.reduce.calTwFlat:main',
                            'calGainMap=papi.reduce.calGainMap:main',
                            'dxtalk=papi.reduce.dxtalk:main',
                            'makeobjmask=papi.reduce.makeobjmask:main',
                            'photometry=papi.photo.photometry:main',
                            'correctNonLinearity=papi.reduce.correctNonLinearity:main',
                            'remove_cosmics=papi.reduce.remove_cosmics:main',
                            'modFITS=papi.misc.modFITS:main',
                            'genLogsheet=papi.misc.genLogsheet:main',
                            'collapse=papi.misc.collapse:main',
                            'checkQuality=papi.reduce.checkQuality:main',
                            'eval_focus_serie=papi.reduce.eval_focus_serie:main',
                            'imtrim=papi.misc.imtrim:main']
    },
    data_files=[('resources',
                              ['papi/QL/resources/logo_PANIC.jpg',
                              'papi/QL/resources/logo_PANIC_100.jpg',
                              'papi/QL/resources/ds9.png',
                              'papi/QL/resources/aladin_large.gif']),
                ('config_files',
                            ['papi/config_files/papi.cfg']),
                ('irdr_bin',
                            ['papi/irdr/bin/skyfilter',
                             'papi/irdr/bin/dithercubemean',
                             'papi/irdr/bin/gainmap'])
                ],
    # To compile .ui and .qrc files
    cmdclass=cmdclass
)
