"""
support library to ease dict & JSON management
- dictionary manipulation (extraction, merge, ...)
- json file load, save, update
"""

import json
from datetime import datetime

from vbrpytools import exceptions as vbrExceptions
from vbrpytools.misctools import open_preserve



def sub_dict(input_dict, master_key, sub_keys : list = None):
    """ Retrieve a subdict of a given dic "master" key
        If no input list, retrieve all keys

        @args:
        input_dict -- input dictionary
        master_key -- str
                      the master key to retrieve the subdict from
        sub_keys   -- [.] -- []
                      list of keys to retrieve
    """
    master_dict = input_dict[master_key]
    if sub_keys is None or sub_keys == []:
        sub_dic = master_dict
    else:
        sub_dic = {k: v for k, v in master_dict.items() if k in sub_keys}
    return sub_dic



def merge_dict(dict_a, dict_b, path=None, list_conflict:str=None, overwrite_conflict:bool=False):
    """merges 2 dictionaries, dict_b into dict_a
    Recurse all dictionary keys.
    When dict_a & dict_b have same key, behavior depends on overwrite_conflict & list_conflict

    @args:
        dict_a:             original dictionary into which new content is added
        dict_b:             dictionary to merge into dict_a
        path:               path captured for error raising

        list_conflict:      when dict_a & dict_b have same key that are list...
                            - if None, applies overwrite_conflict
                            - if 'a', appends dict_a & dict_b list elements
                            - if 'u', appends UNIQUE dict_a & dict_b list elements
                              raises an exception if dict_a or dict_b contains duplicated values

        overwrite_conflict: when dict_a & dict_b have same key that are not a dictionary
                            (and not a list when list_conflict is different from None) ...
                            - if true, overwrites dict_a value with dict_b
                            - if false, raises an exception
    """
    if  list_conflict is not None and list_conflict != 'a' and  list_conflict != 'u':
        raise vbrExceptions.OtherException("list_conflict parameter unknown (None, 'a' or 'u'): "
                                               + list_conflict)

    path = path or []

    if not dict_a:
        return dict_b

    for key in dict_b:
        if key not in dict_a:
            dict_a[key] = dict_b[key]
        elif dict_a[key] == dict_b[key]:
            pass # same leaf value
        elif isinstance(dict_a[key], dict) and isinstance(dict_b[key], dict):
            merge_dict(dict_a[key],
                       dict_b[key],
                       path + [str(key)],
                       list_conflict,
                       overwrite_conflict)
        elif (    isinstance(dict_a[key], list)
              and isinstance(dict_b[key], list)
              and list_conflict is not None):
            if list_conflict == 'a':
                dict_a[key] = dict_a[key] + dict_b[key]
            else:
                # list_conflict = 'u'. if any duplicate in dict_a or dict_b -> raises exception
                if len(set(dict_a[key])) != len(dict_a[key]):
                    raise vbrExceptions.OtherException('dict_a list contains duplicate at',
                                                       '.'.join(path + [str(key)]), ':',
                                                       dict_a[key])
                if len(set(dict_b[key])) != len(dict_b[key]):
                    raise vbrExceptions.OtherException('dict_b list contains duplicate at',
                                                       '.'.join(path + [str(key)]), ':',
                                                       dict_b[key])

                dict_a[key] = list(set(dict_a[key]) | set(dict_b[key]))
        elif overwrite_conflict:
            dict_a[key] = dict_b[key]
        else:
            raise vbrExceptions.OtherException('Conflict at', '.'.join(path + [str(key)]))
    return dict_a


def create_nested_dict(keys, last_key_val):
    ''' Creates a dic from a list of key by nesting them

    @args:
        keys:           list of keys to nest
        last_key_val:   value of the last key
    '''
    value = last_key_val
    for key in reversed(keys):
        value = {key:  value}
    return value


def dict_keys_to_int(dict_a):
    """transform all relevant dictionary keys from string to integer
    Recurse all keys.

    @args:
        dict_a: original list into which new content is added
    """
    for key in list(dict_a.keys()):
        if isinstance(key, str) and key.isnumeric():
            actual_key = int(key)
            dict_a[actual_key] = dict_a[key]
            dict_a.pop(key)
        else:
            actual_key = key

        if isinstance(dict_a[actual_key], dict):
            dict_keys_to_int(dict_a[actual_key])
    return dict_a


def load_json_file(filename, key_as_int:bool=True, abort_on_file_missing = True):
    """Load a json file into a dictionary with key conversion
    Supports empty file

    @args:
        filename:               file where to store content
        key_as_int:             if true, convert all relevant keys to integers
        abort_on_file_missing:  if true and file is missing raise an exception, otherwise, return None
    """
    try:
        json_data = {}
        with open_preserve(filename, 'r') as file_ptr:
            # read file as raw string, to be able to check if file is empty
            # if this was not done, json dump will raise JSONDecodeError
            file_raw = file_ptr.read()
            if len(file_raw) > 0:
                json_data = json.loads(file_raw)
                if key_as_int:
                    json_data = dict_keys_to_int(json_data)

        return json_data
    except FileNotFoundError:
        if abort_on_file_missing:
            raise
        return None



class _JsonCustomEncoder(json.JSONEncoder):
    ''' Custom json encoder to bypass default encoder not supporting:
        - set
        - datetime
    '''
    def default(self, o):
        ''' force set to list
        '''
        if isinstance(o, set):
            return list(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


def append_json_file(filename, new_data, indent = 4, **kwargs):
    """Append a json dictionary to an existing json file
    recurse in all keys.
    Supports empty file
    Supports input date containing Sets (transformed as Lists)

    @args:
        filename:       file where to store content
        new_data:       content to put in file
        indent:         formating of json file

    @keyword_args:
        All Optional keyword arguments that merge_dict() takes.
    """
    old_data = load_json_file(filename, key_as_int=True)

    merge_dict(old_data, new_data, **kwargs)
    with open_preserve(filename, 'w', encoding="utf-8", preserve = False) as file_ptr:
        json.dump(old_data, file_ptr, indent = indent, cls = _JsonCustomEncoder)


def save_json_file(output, output_file, preserve = True):
    ''' Dump a dictionary in a json file.
    If requested, keep existing file (renamed with timestamp).
    Supports input date containing Sets (transformed as Lists)

    @args:
        output:         dictionary to save
        output_file:    path of the file, with extension
        preserve:       if True and if {output_file_base}.json exists
                        rename existing by adding timestamp to it
    '''
    # create output file, handling overwriting exising one
    with open_preserve(output_file, 'w', encoding="utf-8", preserve = preserve) as file_ptr:
        json.dump(output, file_ptr, indent = 4, cls = _JsonCustomEncoder)

if __name__ == '__main__':
    raise vbrExceptions.OtherException('This module should not be called directly.')
