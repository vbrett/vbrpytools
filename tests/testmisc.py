'''
test misc functions
'''

# import time
from pathlib import Path
from vbrpytools import misctools

if __name__ == "__main__":
    # l = range(1, 80, 1)
    # for n in misctools.iterate_and_display_progress(l, prefix = 'Processing'):
    #     time.sleep(0.02)

    # for revolve_id in range(0, 10):
    #     ll = misctools.divide_list(range(1, 40, 1), 1)
    #     for n in misctools.iterate_and_display_progress(ll, suffix = 'Processing', revolving_char_id = revolve_id):
    #         time.sleep(0.05)

    print(misctools.colorize('This is a test', misctools.Colors.RED))
    print(misctools.colorize('This is a test', misctools.Colors.BLACK + misctools.Colors.BG_WHITE + misctools.Colors.BOLD))
    print(misctools.colorize('This is a test', misctools.Colors.ITALIC + misctools.Colors.BG_YELLOW))
    print(misctools.colorize('This is a test', misctools.Colors.GREEN + misctools.Colors.BG_BLUE))

    tf = misctools.open_preserve(Path("./test_create/test.txt"), "w")
    tf.close()
