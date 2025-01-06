'''
test misc functions
'''

import time

from vbrpytools import misctools

if __name__ == "__main__":
    l = range(1, 80, 1)
    for n in misctools.iterate_and_display_progress(l, prefix = 'Processing'):
        time.sleep(0.02)

    for revolve_id in range(0, 10):
        ll = misctools.divide_list(range(1, 40, 1), 1)
        for n in misctools.iterate_and_display_progress(ll, suffix = 'Processing', revolving_char_id = revolve_id):
            time.sleep(0.05)
