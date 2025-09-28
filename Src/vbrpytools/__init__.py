""" Package init
"""
import sys
min_ver = (3,10)
if sys.version_info < min_ver :
    raise ValueError(f'incompatible python version. {min_ver} at least needed.',
                     sys.version_info)

__version__ = "v3.6.0"
