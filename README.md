<font size="8">vbrpytools</font>

vbrpytools is a Python library of general functions that I use in all my other packages.

- [Installation](#installation)
- [Use Package](#use-package)
  - [misctools](#misctools)
  - [dicjsontools](#dicjsontools)
  - [exceltojson](#exceltojson)
- [Develop Package](#develop-package)
- [Build Package](#build-package)
  - [Install Build environment](#install-build-environment)
  - [Create Package distribution](#create-package-distribution)
- [License](#license)

# Installation

```bash
pip install vbrpytools
```

⚠️ **This package is not available in Python Package Index (pyPI)**  
Be sure to have one of these environment variables defined to the local repository of this package before installing it:
| variable   | usage  |
| -------- | ------- |
| *PIP_EXTRA_INDEX_URL* | used when defining a local pip server where packages are managed |
| *PIP_FIND_LINKS* | pointing when defining a local folder where packages are archived |

# Use Package

Functions are grouped in the following modules:

## misctools

Support library to ease development
* verbose management
* progress bar display
* open with file preservation
* input argument management
* command line execution
* Handling stdout encoding to match PYTHONIOENCODING envvar (needed when bundling python script in a exe)

```python
from vbrpytools import misctools

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

## dicjsontools

Support library to ease dict & JSON management:
* dictionary manipulation (extraction, merge, ...)
* json file load, save, update

```python
from vbrpytools import dicjsontools

# Retrieve a subdict of a given dic "master" key
dicjsontools.sub_dict(dic, key, subkeys)

# merges 2 dictionaries, dict_b into dict_a
dicjsontools.merge_dict(dic_a, dic_b, options)

# Creates a dic from a list of key by nesting them
dicjsontools.create_nested_dict(keys, last_key_val)

# transform all relevant dictionary keys from string to integer
dicjsontools.dict_keys_to_int(dic)

# Load a json file into a dictionary with key conversion
dicjsontools.load_json_file(filename)

# Append a json dictionary to an existing json file
dicjsontools.append_json_file(filename, dic)

# Dump a dictionary in a json file
dicjsontools.save_json_file(dic, filename)
```

## exceltojson

Open an excel file table and save it as a json file
Available as executable script.

```bash
exceltojson *args*
python -m exceltojson *args*
```

# Develop Package

* Clone the project repo
* Create a python venv in the cloned project
* In this venv, install the [package as editable](https://setuptools.pypa.io/en/latest/userguide/development_mode.html)
  ```bash
  pip install --editable .
  ```
* Treat yourself!

# Build Package

This package is built with [Hatch](https://hatch.pypa.io).

## Install Build environment

See [Hatch installation](https://hatch.pypa.io/latest/install/).

It is recommanded to have hatch installed either using installer or as a python package in isolated environment using pipx.

* <ins>*Installer method*<ins>

  ⚠️ **This requires admin rights.**

  Download and run the installer using the standard Windows msiexec program, specifying one of the `.msi` files as the source. Use the `/passive` and `/i` parameters to request an unattended, normal installation.

  `msiexec /passive /i https://github.com/pypa/hatch/releases/latest/download/hatch-x64.msi`

* <ins>*Python package method*<ins>

  ⚠️ **This requires Python to be installed.**

  [pipx](https://pipx.pypa.io/) allows for the global installation of Python applications in isolated environments.

  1. [Install](https://pipx.pypa.io/stable/installation/) pipx:\
  `py -m pip install --user pipx`

  1. It is possible (even most likely) the above finishes with a WARNING looking similar to this:\
  `WARNING: The script pipx.exe is installed in '<USER folder>\AppData\Roaming\Python\Python3x\Scripts' which is not on PATH`\
  If so, go to the mentioned folder, allowing you to run the pipx executable directly. Enter the following line (even if you did not get the warning):\
  `.\pipx.exe ensurepath`\
  This will add necessary paths to your search path. Restart your terminal session and verify pipx does run.

  1. install hatch using this command:\
    `pipx install hatch`

## Create Package distribution

From a command line in the root directory of this project, launch build
```bash
hatch build -t sdist -t wheel -t pyinstaller
```

And you're done!  
3 formats are created:
* sdist (.tar.gz archive)
* wheel (.whl archive)
* binary (.exe archive)

# License

ref: [LICENSE](.\LICENSE)
`vbrpytools` is distributed under the terms of MIT.