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
from threading import Thread
from pathlib import Path
from time import sleep
import sys
from msvcrt import getch, kbhit
import random
import subprocess
import traceback
import inspect
from argparse import ArgumentParser, RawTextHelpFormatter
from functools import wraps
from datetime import datetime

import humanize

from vbrpytools import exceptions as vbrExceptions


# VERBOSE RELATED FUNCTIONS
# =========================
LOG_START = '>>>'
LOG_STOP = '<<<'
REVOLVING_SEQUENCES = [['-', '-', '\\', '\\', '|', '|', '/', '/'],
                       [".",".","o","o","O","O","*","*"," "," "],
                       ['•●•', '•●•', '••●', '••●', '●••', '●••'],
                       ["( ●  )","(  ● )","(   ●)","(  ● )","( ●  )","(●   )"],
                       ["⢎ ","⠎⠁","⠊⠑","⠈⠱"," ⡱","⢀⡰","⢄⡠","⢆⡀"],
                       ['⣷','⣯','⣟','⡿','⢿','⣻','⣽','⣾'],
                       ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"],
                       ["⠁","⠂","⠄","⡀","⡈","⡐","⡠","⣀","⣁","⣂","⣄","⣌","⣔","⣤","⣥","⣦","⣮","⣶","⣷","⣿","⡿","⠿","⢟","⠟","⡛","⠛","⠫","⢋","⠋","⠍","⡉","⠉","⠑","⠡","⢁"],
                       ["🕛","🕐","🕑","🕒","🕓","🕔","🕕","🕖","🕗","🕘","🕙","🕚"],
                      ]

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
        try:
            func_name = func.__name__
        except AttributeError:
            func_name = 'function'

        # print function name & arguments (minus "self" argument)
        log_repeat = 20
        if is_verbose:
            print(LOG_START * log_repeat)
            print(f"{LOG_START} {func_name}()")
            argv_name = inspect.getfullargspec(func).args
            is_method = argv_name[0].lower() == 'self' # Not a very clean way, as it relies on always naming 1st method arg 'self'
            if len(args) > (0 if not is_method else 1):
                argv_name = argv_name[1:] if is_method else argv_name
                argv_val = args[1:] if is_method else args
                print( f'{LOG_START} args:\n{LOG_START}    - ' \
                      + f'\n{LOG_START}    - '.join([f'{argv_name[i]} : {str(v)}' for i,v in enumerate(argv_val)]))
            if len(kwargs) > 0:
                print(f'{LOG_START} kwargs:\n{LOG_START}    - ' + f'\n{LOG_START}    - '.join([f'{k} : {str(v)}' for k, v in kwargs.items()]))
            start_time = datetime.now()
            print(LOG_START * log_repeat)

        result = func(*args, **kwargs)

        # print function execution time & output
        if is_verbose:
            elapsed_time = datetime.now() - start_time
            hum_elapsed_time = humanize.precisedelta(elapsed_time)
            printed_result = f'{LOG_STOP} Result: ' \
                           + (f'{str(result)[:int(verbose_truncate/2)]}\n{LOG_STOP} (...)\n{LOG_STOP} {str(result)[-int(verbose_truncate/2):]}'
                              if len(str(result)) > verbose_truncate > 0
                              else str(result))
            print(LOG_STOP * log_repeat)
            print(f'{LOG_STOP} {func_name}()')
            print(f'{LOG_STOP} Executed in {hum_elapsed_time}')
            print(printed_result)
            print(LOG_STOP * log_repeat)

        return result
    return wrap


def with_waiting_message(**deco_kwargs):
    """ decorator to display a moving waiting message while executing

    @kwargs:
        see run_and_display_progress
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*func_args, **func_kwargs):
            return run_and_display_progress(target=func,
                                            target_args=func_args,
                                            target_kwargs=func_kwargs,
                                            **deco_kwargs)
        return wrapper
    return decorator


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
        display_pb          - Optional - True : choose to iterate with or without
                                                displaying the progress bar(bool)
        revolving_seq_id    - Optional - None : id of the revolving sequence to use.
                                                Random id if not defined
                                                if > number of revolving sequence, get using modulo %

    @constants:
        print_end           - Hidden  - '\r'  : end character (e.g. "\r") (Str)
        decimals            - Hidden  - 2     : (only for progress bar)    positive number of decimals in percent complete (Int)
        length              - Hidden  - 50    : (only for progress bar)    character length of bar (Int)
        fill                - Hidden  - '█'   : (only for progress bar)    bar fill character (Str)
        empty               - Hidden  - '-'   : (only for progress bar)    bar empty character (Str)
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
    revolving_seq = REVOLVING_SEQUENCES[kwargs.get('revolving_seq_id',
                                                   random.randrange(0, len(REVOLVING_SEQUENCES)))
                                        % len(REVOLVING_SEQUENCES)
                                       ]

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
            progress = f'{revolving_seq[actual_iteration % len(revolving_seq)]}'
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

def run_and_display_progress(target, target_args=(), target_kwargs=None,
                             **kwargs):
    """ Run a target function in a separate thread and return function return value once complete.
    If stdout is a tty, display a revolving sequence during execution.

    @return: target return value

    @args
        target:         function to run in a separate thread
        target_args:    arguments to pass to the target function
        target_kwargs:  keyword arguments to pass to the target function

    @kwargs:
        progress_message    - Optional - 'executing <function name>': message string (Str) displayed during progress
        end_message         - Optional - '<function name> executed' : message string (Str) displayed once execution is complete, overwriting the progress message
        wait_time           - Optional - 0.2s                       : time to wait between checks if the thread is still alive
        revolving_seq_id    - Optional - None                       : id of the revolving sequence to use.
                                                                      Random id if not defined
                                                                      if > number of revolving sequence, get using modulo %
    """
    stdout_on_console = sys.stdout.isatty()

    class ThreadWithReturn(Thread):
        """ Custom Thread class that returns the target function return value """
        def __init__(self, group=None, target=None, name=None,
                     target_args=(), target_kwargs=None, daemon=None):
            """ Custom Thread class that returns the target function return value """
            # Initializing the Thread class
            super().__init__(group=group, target=target, name=name,
                             args=target_args, kwargs=target_kwargs, daemon=daemon)
            self._return = None

        def run(self):
            """ Overriding Thread.run function to retrieve the target function return value """
            try:
                if self._target is not None:
                    self._return = self._target(*self._args, **self._kwargs)
            finally:
                # Avoid a refcycle if the thread is running a function with
                # an argument that has a member that points to the thread.
                del self._target, self._args, self._kwargs

        def join(self, timeout=None):
            """ Overriding Thread.join function to pass the target function return value """
            super().join(timeout)
            return self._return

    try:
        target_name = target.__name__
    except AttributeError:
        target_name = 'target'

    progress_message = kwargs.get('progress_message', f"Executing {target_name}")
    end_message = kwargs.get('end_message', f"{target_name} executed.")
    wait_time = kwargs.get('wait_time', 0.2)
    revolving_seq_id = kwargs.get('revolving_seq_id', random.randrange(0, len(REVOLVING_SEQUENCES))) % len(REVOLVING_SEQUENCES)

    revolving_seq = REVOLVING_SEQUENCES[revolving_seq_id]
    prev_progress_len = 0
    actual_iteration = 0
    return_val = None

    # Create a thread to run the target function
    thread = ThreadWithReturn(target = target, target_args = target_args, target_kwargs = target_kwargs)
    thread.start()
    # Wait for the thread to finish
    while thread.is_alive():
        if stdout_on_console:
            progress = ' '.join(['\r', progress_message, revolving_seq[actual_iteration % len(revolving_seq)]])
             # add spaces to erase trailing characters on a tty
            progress += ' ' * max([0, prev_progress_len - len(progress)])
            prev_progress_len = len(progress)
            print(progress, end='\r', flush=True)
            actual_iteration += 1
        return_val = thread.join(wait_time)

    if stdout_on_console:
        # add spaces to erase trailing characters on a tty
        end_message += ' ' * max([0, prev_progress_len - len(end_message)])
    print(end_message)
    return return_val


def _isansitty() -> bool:
    """ Check if terminal supports ANSI escape codes
    The response to \x1B[6n should be \x1B[{line};{column}R according to
    https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797. If this
    doesn't work, then it is unlikely ANSI escape codes are supported.
    """
    if not sys.stdout.isatty():            # if stdout is not a tty, ANSI won't work
        return False

    while kbhit():                         # clear stdin before sending escape in
        getch()                            # case user accidentally presses a key

    sys.stdout.write("\x1B[6n")            # alt: print(end="\x1b[6n", flush=True)
    sys.stdout.flush()                     # double-buffered stdout needs flush
    sleep(0.000005)                        # wait 5usec to ensure kbhit will catch the response

    sys.stdout.write('\b\b\b\b')           # move cursor back to avoid printing garbage chars in console
    sys.stdin.flush()                      # flush stdin to make sure escape works
    if kbhit():                            # ANSI won't work if stdin is empty
        if ord(getch()) == 27 and kbhit(): # check that response starts with \x1B[
            if getch() == b"[":
                while kbhit():             # read stdin again, to remove the actual
                    getch()                # value returned by the escape

                return True                # ANSI works so True should be returned.
    return False                           # Otherwise, return False

class Colors:
    """ Colors for the terminal """
    # Text colors - foreground
    BLACK = '\033[90m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

    # Text colors - background
    BG_BLACK = '\033[100m'
    BG_RED = '\033[101m'
    BG_GREEN = '\033[102m'
    BG_YELLOW = '\033[103m'
    BG_BLUE = '\033[104m'
    BG_PURPLE = '\033[105m'
    BG_CYAN = '\033[106m'
    BG_WHITE = '\033[107m'

    # Text formatting
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'

    # Reset
    ENDC = '\033[0m'


def colorize(text: str, color):
    """ Colorize text if possible """
    if not _isansitty():
        return text
    return f"{color}{text}{Colors.ENDC}"



# MISC FUNCTIONS
# ==============
def timestamp_filename(file):
    """ Rename a file by adding a timestamp to its name """
    file = Path(file)
    if file.exists():
        # rename existing file by adding timestamp to its name
        file.rename(file.parent / (file.stem + datetime.now().strftime('_%y-%m-%dT%H.%M.%S') + file.suffix))

def open_preserve(file, mode, *args, encoding='utf-8', preserve = True, create_path_if_w = True, **kwargs):
    ''' Open a file
    If mode is write and create_path_if_w is requested, create path if it does not exist.
    If mode is write and preserve is requested, existing file is preserved under a different name (= original name + timestamp).
    Enforce encoding - to UTF-8 by default

    @returns: file object

    @args:
    same as output

    @kwargs:
    preserve -- bool -- True
                if True and mode is write and file exists
                rename existing file by adding timestamp to it

    create_path_if_w -- bool -- True
                if True and mode is write, create path if it does not exist
    same as output
    '''
    file = Path(file)
    if 'w' in mode.lower():
        if create_path_if_w and not file.parent.exists():
            file.parent.mkdir(parents = True, exist_ok = True)

        if preserve :
            timestamp_filename(file)

    return open(file, mode, *args, encoding = encoding, **kwargs)


def get_args(args_def, display_value = True):
    """ all-in-one argument definition, parse & read
    @returns - namespace - parsed args
    @args:
        args_def         - Required - [([args], {kwargs}), ...] - list of tuples for each argument to define and handled
        display_value    - Optional - bool                      - if true, display read values
    """
    parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
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
