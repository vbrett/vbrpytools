# vbrsupport

vbrsupport is a Python library of general functions that I start using a bit everywhere.

## Installation

### Normal Usage

Use the local package manager [TBD](TBD) to install vbrsupport.

```bash
pip install vbrsupport
```

### Development Mode

ref: [pypa development mode](https://setuptools.pypa.io/en/latest/userguide/development_mode.html)

* Clone of the project repo
* Create a python venv in the cloned project
* In this venv, install the package as editable
  ```bash
  pip install --editable .
  ```

## Usage

Functions are grouped in the following modules:

### misctools

Support library to ease development
* verbose management
* progress bar display
* open with file preservation
* input argument management
* command line execution
* Handling stdout encoding to match PYTHONIOENCODING envvar (needed when bundling python script in a exe)

```python
from vbrsupport import misctools

# decorator to manage verbose & display execution information
@misctools.with_verbose

# Call in a loop to create terminal progress bar or revolving character
misctools.iterate_and_display_progress(iterable)

# Make a copy of an existing file before opening it in write mode + enforce encoding to UTF-8 by default
misctools.open_preserve(filename)

# all-in-one argument definition, parse & read
misctools.get_args(arg_defs)

# Yields successive chunks from a list until all is parsed
misctools.divide_list(list, size)

# Put the input string in the clipboard
misctools.copy_to_clipboard(string)

# If program is running in piping mode enforce stdout encoding to PYTHONIOENCODING.
misctools.force_stdout_encoding()

# Execute a command line in a separate subprocess and return the STD OUT
misctools.execute_cmd(cmd)

# Ask a yes/no question via and return answer.
misctools.query_yes_no(question)

# Transform a string into a date, trying to decode it.
misctools.parse_str_date(string)
```

### dicjsontools

Support library to ease dict & JSON management:
* dictionary extraction & merge
* json file load, save, update

```python
from vbrsupport import dicjsontools

# Retrieve a subdict of a given dic "master" key
dicjsontools.sub_dict(dic, key, subkeys)

# merges 2 dictionaries, dict_b into dict_a
dicjsontools.merge_dict(dic_a, dic_b, options)

# transform all relevant dictionary keys from string to integer
dicjsontools.dict_keys_to_int(dic)

# Load a json file into a dictionary with key conversion
dicjsontools.load_json_file(filename)

# Append a json dictionary to an existing json file
dicjsontools.append_json_file(filename, dic)

# Dump a dictionary in a json file
dicjsontools.save_json_file(dic, filename)
```

### exceltojson

Open an excel file table and save it as a json file
Available as executable script.

```bash
exceltojson *args*
python -m exceltojson *args*
```

## License

[Veoneer TBD](TBD)