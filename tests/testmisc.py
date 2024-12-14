'''
test misc functions
'''

import time

from vbrpytools import misctools

if __name__ == "__main__":
    l = range(1, 80, 1)
    ll = misctools.divide_list(l, 1)
    for n in misctools.iterate_and_display_progress(l, prefix = 'Processing'):
        time.sleep(0.05)
    for n in misctools.iterate_and_display_progress(ll, suffix = 'Processing'):
        time.sleep(0.05)
