'''
test exceltojson functions
'''

import sys
from time import sleep
from vbrpytools import exceltojson


def _main():
    """Main function to test exceltojson functions."""
    sys.argv = [sys.argv[0],
                '-f', 'tests/resources/test.xlsx',
                '-t', 'suivi',
                '-o', 'tests/outputs/output.json',
                '-p']
    exceltojson._main() #pylint: disable=protected-access #accessed for test purpose only

    sleep(2)
    sys.argv = [sys.argv[0],
                '-f', 'tests/resources/test.xlsx',
                '-t', 'other',
                '-o', 'tests/outputs/output.json',
                '-p', '-a']
    exceltojson._main() #pylint: disable=protected-access #accessed for test purpose only

    sleep(2)
    sys.argv = [sys.argv[0],
                '-f', 'tests/resources/test.xlsx',
                '-t', 'suivi,other',
                '-o', 'tests/outputs/output.json',
                '-p']
    exceltojson._main() #pylint: disable=protected-access #accessed for test purpose only

if __name__ == "__main__":
    # run the test
    _main()
