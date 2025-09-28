'''
test exceltojson functions
'''

import sys
from vbrpytools import exceltojson


def _main():
    """Main function to test exceltojson functions."""
    sys.argv = [sys.argv[0],
                '-f', 'tests/resources/test.xlsx',
                '-t', 'suivi',
                '-o', 'tests/outputs/output.json',
                '-p']
    exceltojson._main() #pylint: disable=protected-access #accessed for test purpose only

if __name__ == "__main__":
    # run the test
    _main()
