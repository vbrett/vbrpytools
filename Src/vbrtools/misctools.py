"""
support library to ease development
- verbose management
- progress bar display
- open with file preservation
- input argument management
- command line execution
- Handling stdout encoding to match PYTHONIOENCODING envvar (needed when bundling python script in a exe)
...
"""

import os
import sys
import random
import subprocess
import traceback
import inspect
from argparse import ArgumentParser
from functools import wraps
from datetime import datetime

import humanize

from vbrtools import exceptions as vbrExceptions


# ARGS & VERBOSE RELATED FUNCTIONS
# ================================

def with_verbose(func):
    """ decorator to manage verbose & display execution information
    - Verbose is initialized by setting initial_verbose_lvl in func kwargs
        - initial_verbose_lvl = 0 means that verbose is inactive
        - initial_verbose_lvl > 0 means that verbose is active
        - initial_verbose_lvl > 1 means that verbose is active and called functions will also be verbose
    - Verbose level is passed through function tree using _next_verbose_lvl kwarg
    - Decorator update func kwargs:
        - update next level verbose (_next_verbose_lvl)
        - define if progress bar can be displayed or not (display_pb), which is not possible if lvl > 1
            (means that there can be a lower level function with verbose)
        - add a printverbose function that can be used by func to print verbose

    If verbose is active, decorator prints:
    - function name & arguments at entry (excluding "self" argument)
    - result & processing time at exit

    @keyword_args:
    initial_verbose_lvl -- int  -- 0
                        The initial level to start verbose
    verbose_truncate    -- int -- 500
                        if > 0, truncate result up to verbose_truncate character
    """
    @wraps(func)
    def wrap(*args, **kwargs):
        # Manage verbose kwargs
        #   - Load level: either existing _next_verbose_lvl otherwise initial_verbose_lvl
        #   - Define if verbose is active
        #   - Compute next verbose level
        #   - Create printverbose function
        #   - Define if progress bar can be displayed
        #   - Save computed values in kwargs if they were already present
        verbose_lvl = kwargs.get('_next_verbose_lvl', kwargs.get('initial_verbose_lvl', 0))
        is_verbose = verbose_lvl > 0
        verbose_truncate = kwargs.get('verbose_truncate', 500)
        kwargs['_next_verbose_lvl'] = max([verbose_lvl - 1, 0])
        kwargs['display_pb'] = kwargs.get('display_pb', True) and (verbose_lvl <= 1) # display pb only if not verbose or last verbose level
        kwargs['verboseprint'] = print if is_verbose else lambda *a, **k: None #function to print verbose

        # print function name & arguments (minus "self" argument)
        log_repeat = 20
        if is_verbose:
            log_start = '>>>'
            print(log_start * log_repeat)
            print(f"{log_start} {func.__name__}()")
            argv_name = inspect.getfullargspec(func).args
            is_method = argv_name[0].lower() == 'self' # Not a very clean way, as it relies on always naming 1st method arg 'self'
            if len(args) > (0 if not is_method else 1):
                argv_name = argv_name[1:] if is_method else argv_name
                argv_val = args[1:] if is_method else args
                print( f'{log_start} args:\n{log_start}    - ' \
                      + f'\n{log_start}    - '.join([f'{argv_name[i]} : {str(v)}' for i,v in enumerate(argv_val)]))
            if len(kwargs) > 0:
                print(f'{log_start} kwargs:\n{log_start}    - ' + f'\n{log_start}    - '.join([f'{k} : {str(v)}' for k, v in kwargs.items()]))
            start_time = datetime.now()
            print(log_start * log_repeat)

        result = func(*args, **kwargs)

        # print function execution time & output
        if is_verbose:
            log_stop = '<<<'
            end_time = datetime.now()
            elapsed_time = end_time - start_time
            hum_elapsed_time = humanize.precisedelta(elapsed_time)
            printed_result = f'{log_stop} Result: ' \
                           + (f'{str(result)[:int(verbose_truncate/2)]}\n{log_stop} (...)\n{log_stop} {str(result)[-int(verbose_truncate/2):]}'
                              if len(str(result)) > verbose_truncate > 0
                              else str(result))
            print(log_stop * log_repeat)
            print(f'{log_stop} {func.__name__}()')
            print(f'{log_stop} Executed in {hum_elapsed_time}')
            print(printed_result)
            print(log_stop * log_repeat)

        return result
    return wrap

def iterate_and_display_progress(iterable, prefix = '', suffix = '', **kwargs):
    r"""
    Call in a loop to create terminal progress bar or revolving character
    Note that you should not print anything else while using this progress bar.
    Otherwise, it will not refresh the same terminal line

    If the input iterable has length, display a progress bar,
    otherwise (for example with a generator), display a revolving character

    Based on https://stackoverflow.com/questions/3173320

    @args:
        iterable    - Required        : iterable object (Iterable)
        prefix      - Optional - ''   : prefix string (Str)
        suffix      - Optional - ''   : suffix string (Str)

    @kwargs:
        display_pb  - Optional - True : choose to iterate with or without
                                        displaying the progress bar(bool)

    @constants:
        print_end       - Hidden  - '\r'  : end character (e.g. "\r") (Str)
        decimals        - Hidden  - 2     : (only for progress bar)    positive number of decimals in percent complete (Int)
        length          - Hidden  - 50    : (only for progress bar)    character length of bar (Int)
        fill            - Hidden  - '█'   : (only for progress bar)    bar fill character (Str)
        empty           - Hidden  - '-'   : (only for progress bar)    bar empty character (Str)
        revolving_char  - Hidden  - '-\|/': (only for revolving char ) character sequence to create the revolving character (list)
    """
    stdout_on_console = sys.stdout.isatty()
    try:
        total = len(iterable)
    # handle the case the iterator has no length (generator for example)
    except TypeError:
        total = -1

    print_end = "\r"
    # progress bar parameters
    decimals = 2
    length = 50
    fill = '█'
    empty = '-'
    # Revolving character parameters
    revolving_char_list = [['-', '\\', '|', '/'],
                           [" ",".","o","O","*"," "],
                           ['•●•', '••●', '●••'],
                           ["( ●  )","(  ● )","(   ●)","(  ● )","( ●  )","(●   )"],
                           ["⢎ ","⠎⠁","⠊⠑","⠈⠱"," ⡱","⢀⡰","⢄⡠","⢆⡀"],
                           ['⣾','⣽','⣻','⢿','⡿','⣟','⣯','⣷'],
                           ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"],
                           ["⠁","⠂","⠄","⡀","⡈","⡐","⡠","⣀","⣁","⣂","⣄","⣌","⣔","⣤","⣥","⣦","⣮","⣶","⣷","⣿","⡿","⠿","⢟","⠟","⡛","⠛","⠫","⢋","⠋","⠍","⡉","⠉","⠑","⠡","⢁"],
                           ["🕛","🕐","🕑","🕒","🕓","🕔","🕕","🕖","🕗","🕘","🕙","🕚"]
                          ]
    revolving_char = revolving_char_list[random.randrange(0, len(revolving_char_list))]

    def print_progress(iteration):
        ''' Progress Printing Function, use -1 to print final progress
            bypassed if display_pb is False or if iterable size is 0
        '''
        if not kwargs.get('display_pb', True) or total == 0:
            # display progress is deactivated or iterable is empty > don't print any progress
            return

        # iteration_count = -1 informs this is the final progress
        actual_iteration = iteration if iteration > -1 else max([0, total])   # max so that = 0 when total = -1

        if total == -1:
            # total length is not known > print a revolving character
            progress = f'{revolving_char[actual_iteration % len(revolving_char)]}'
        else:
            # total length is known > print a progress bar
            percent = ("{0:." + str(decimals) + "f}").format(100 * (actual_iteration / float(total)))
            filled_len = int(length * actual_iteration // total)
            pbar = fill * filled_len + empty * (length - filled_len)
            progress = f'|{pbar}| {percent}%'

        full_progress = ' '.join(['\r', prefix, progress, suffix])
        if iteration == -1:
            # End of iteration, force print without print_end
            print(full_progress)
        elif stdout_on_console:
            # only print if stdout is routed to the console,
            # otherwise it generally means stdout is routed to a file, so it will not work (each iteration will create a new txt line)
            print(full_progress, end = print_end)

    # Update Progress & yield iterated item
    for i, item in enumerate(iterable):
        print_progress(i)
        yield item

    # Print final progress
    print_progress(-1)



# MISC FUNCTIONS
# ==============

def open_preserve(file, mode, *args, encoding='utf-8', preserve = True, **kwargs):
    ''' Open a file and if mode is write and preserve is requested, existing file
    is preserved under a different name (= original name + timestamp).
    Also enforce encoding - to UTF-8 by default

    @returns: file object

    @args:
    same as output

    @kwargs:
    preserve -- bool -- True
                if True and mode is write and file exists
                rename existing file by adding timestamp to it
    same as output
    '''
    if preserve and 'w' in mode.lower() and os.path.exists(file):
        # rename existing file by adding timestamp to its name
        base, ext = os.path.splitext(file)
        ct = datetime.fromtimestamp(os.path.getmtime(file)).strftime('_%y-%m-%dT%H.%M.%S')
        os.rename(file, base + ct + ext)

    return open(file, mode, *args, encoding = encoding, **kwargs)


def get_args(args_def, display_value = True):
    """ all-in-one argument definition, parse & read
    @returns - namespace - parsed args
    @args:
        args_def         - Required - [([args], {kwargs}), ...] - list of tuples for each argument to define and handled
        display_value    - Optional - bool                      - if true, display read values
    """
    parser = ArgumentParser()
    for args, kwargs in args_def:
        parser.add_argument(*args, **kwargs)
    args = parser.parse_args()

    if display_value:
        log_arg = '=' * 60
        print(log_arg)
        print("launching function with these parameters:")
        for k, v in vars(args).items():
            print(k, ":", v)
        print(log_arg)
    return args

def divide_list(lst, size):
    '''Yields successive chunks from lst until all lst is parsed
    @returns - N/A (generator)
    @args:
        lst     - list - list of elements to split
        size    - int  - size of each split
    '''
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

def copy_to_clipboard(input_str: str):
    """Put the input string in the clipboard
    """
    subprocess.run(['clip.exe'], input=input_str.strip().encode('utf-16'), check=True)

def force_stdout_encoding():
    """
        If program is running in piping mode (and not in terminal mode), check if stdout encoding matches
        PYTHONIOENCODING environment variable. If not, enforce stdout to its value.
    """
    if sys.stdout.isatty() is False:
        # piping mode > try to read PYTHONIOENCODING. If it is not defined (=False), nothing to do.
        try:
            python_io_encoding = str(os.environ["PYTHONIOENCODING"])
            # replace utf8 per utf-8 to allow comparing with current stdout encoding (utf8 and utf-8 values seem interchangeable)
            if python_io_encoding.lower() == "utf8":
                python_io_encoding = "utf-8"
        except KeyError:
            python_io_encoding = False

        if python_io_encoding is not False:
            if str(sys.stdout.encoding) != python_io_encoding:
                # PYTHONIOENCODING differing from stdout encoding.
                # This should normally not happen unless PyInstaller is still broken. Setting hard utf-8 workaround
                sys.stdout.flush()  # to ensure anything already sent to stdout is displayed
                sys.stdout = open(sys.stdout.fileno(), 'w', encoding='utf-8', closefd=False)

def execute_cmd(cmd, stderr = None, abort_on_error = False, log_error=False):
    """Execute a command line in a separate subprocess and return the STD OUT
       if execution fails, returns error message instead of raising exceptions

    @returns -- (success, -- bool -- true if cmd succeeded
                 output)     str  -- cmd output

    @args:
        cmd:            list of command line arguments to execute
        stderr:         where to direct error pipe. None by default
        abort_on_error: if true, raise exception on error
        log_error:      if true and abort_on_error is false, print error

    @keyword_args:
        N/A
    """
    output = ''
    try:
        output = subprocess.check_output(' '.join(cmd), stderr=stderr, encoding='UTF-8', errors='ignore')
        return True, output
    except subprocess.CalledProcessError as subp:
        if abort_on_error:
            raise
        if log_error:
            print(f'!ERROR! Called Process Error:\n{subp.output}')
        return False, subp.output
    except Exception:# pylint: disable=broad-except
        if abort_on_error:
            raise
        if log_error:
            print(f'!ERROR! Error during execution of subprocess:\n{traceback.format_exc()}')
        return False, traceback.format_exc()



def query_yes_no(question, default=None):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".

    @returns -- bool

    @args:
        question:       question displayed
        default:        default value if user returns no value

    @keyword_args:
        N/A
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError(f"invalid default answer: '{default}'")

    while True:
        choice = input(question + prompt).lower()
        if default is not None and choice == "":
            return valid[default]
        if choice in valid:
            return valid[choice]

        print("Please respond with 'yes/y' or 'no/n'.\n")


def parse_str_date(in_date:str, utc = True):
    ''' Transform a string into a date, trying to decode it.
        Supported formats:
            (YY)YY/MM/DD (hh:mm:ss)
            (YY)YY-MM-DD (hh:mm:ss)
            (YY)YY.MM.DD (hh:mm:ss)
        - Date separator can be '/', '.' or '-'
        - For months & days: only numerical values are supported, not month name or weekday
        - Values shall always be zero-padded
        - Field order is constant year, month, day, hour, minute, second
        - Year can be with or without century
        - Time is optional

    @returns -- aware datetime value - None if in_date is None

    @args:
        in_date:    input string. Can be None
        utc:        if true, consider in_date as UTC, otherwise as local

    @keyword_args:
        N/A
    '''
    #TODO: handle non zero-padded values

    if not in_date:
        return None

    in_date = in_date.replace('.', '-').replace('/', '-')
    in_date += ' 00:00:00' if len(in_date.split(':')) == 1 else ''
    if utc:
        tz = '+0000'
    else:
        tz = datetime.now().astimezone().strftime('%z')
    in_date += tz
    for date_format in ('%Y-%m-%d %H:%M:%S%z', '%y-%m-%d %H:%M:%S%z'):
        try:
            return datetime.strptime(in_date, date_format)
        except ValueError:
            pass
    raise vbrExceptions.OtherException('no valid date format found in', in_date)


if __name__ == '__main__':
    raise vbrExceptions.OtherException('This module should not be called directly.')
