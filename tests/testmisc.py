'''
test misc functions
'''

from time import sleep
from pathlib import Path
from vbrpytools import misctools


@misctools.with_waiting_message(progress_message = 'doing stuff', end_message = 'stuff is done !')
def test_func(nbr):
    """Test function to simulate a long-running process."""
    for i in range(nbr):
        sleep(1)

def _main():
    """Main function to test misc functions."""
    # l = range(1, 80, 1)
    # for n in misctools.iterate_and_display_progress(l, prefix = 'Processing'):
    #     time.sleep(0.02)

    # for revolve_id in range(0, 10):
    #     ll = misctools.divide_list(range(1, 40, 1), 1)
    #     for n in misctools.iterate_and_display_progress(ll, suffix = 'Processing', revolving_char_id = revolve_id):
    #         time.sleep(0.05)

    print(misctools.colorize('This text is red', misctools.Colors.RED))
    print(misctools.colorize('This text is bold on white', misctools.Colors.BLACK + misctools.Colors.BG_WHITE + misctools.Colors.BOLD))
    print(misctools.colorize('This text is italic on yellow', misctools.Colors.ITALIC + misctools.Colors.BG_YELLOW))
    print(misctools.colorize('This text is green on blue', misctools.Colors.GREEN + misctools.Colors.BG_BLUE))

    tf = misctools.open_preserve(Path("./test_create/test.txt"), "w")
    tf.close()

    test_func(10)

if __name__ == "__main__":
    # run the test
    _main()
