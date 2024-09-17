"""
Library for support package exceptions
"""

class OtherException(Exception):
    """General exception for Support package"""


if __name__ == '__main__':
    raise OtherException('This module should not be called directly.')
