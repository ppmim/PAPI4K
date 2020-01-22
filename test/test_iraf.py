import pytest
try:
    from pyraf import iraf
except Exception as OSError:
    pass

import sys

sys.stdin.read(1)

try:
    sys.stdin.read(1)
except Exception as e:
    pass
sys.stdout.write("1")
