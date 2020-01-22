import pytest
from reduce import calDark


files = ["/home/jmiguel/DATA/PANIC2/test_files/Darks_N6_0106.join.fits",
        "/home/jmiguel/DATA/PANIC2/test_files/Darks_N6_0107.join.fits",
        "/home/jmiguel/DATA/PANIC2/test_files/Darks_N6_0108.join.fits"]

temp_directory = "/tmp"


def test_caldark():

    cd = calDark.MasterDark(files, temp_dir=temp_directory)
    out = cd.createMaster()
    assert out == "/tmp/mdark_12_1.fits"

