""" Test init
"""
import sys
min_ver = (3,9)
if sys.version_info < min_ver :
    raise ValueError(f'incompatible python version. {min_ver} at least needed.',
                     sys.version_info)
