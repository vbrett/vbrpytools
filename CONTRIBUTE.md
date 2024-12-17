<font size="8">Development & Build</font>

This provides instructions on how to contribute to the development of this package, and how to build & publish it.

- [Install Develoment environment](#install-develoment-environment)
- [Install Build environment](#install-build-environment)
  - [Installing `hatch` using installer](#installing-hatch-using-installer)
  - [Installing `hatch` as isolated Python Package](#installing-hatch-as-isolated-python-package)
- [Build Project](#build-project)
- [Publish Package](#publish-package)

&nbsp;  

___
# Install Develoment environment

* Clone the project repository on your local machine.
* Create a virtual environement (venv) in the cloned project.
* If this venv is done through VSCode (see [details](https://code.visualstudio.com/docs/python/environments#_creating-environments)), it automatically installs this project and all its dependencies in [editable mode](https://setuptools.pypa.io/en/latest/userguide/development_mode.html).  
If not, then install this package in editable mode:  
`pip install --editable .\`

&nbsp;  

___
# Install Build environment

This package is built with [Hatch](https://hatch.pypa.io) which needs to be installed on the machine first.  
See [Hatch installation instructions](https://hatch.pypa.io/latest/install/).

Notes:
* This procedure is to be done only once per machine. It does not need to be repeated for each project.
* It is recommanded to have `hatch` installed using installer, but this requires admin rights. Instead, it is possile to install `hatch` as a python package.
* If the project is published as standalone executables (that do not require to have Python installed), `hatch` will need a custom version of `hatch-pyinstaller` plugin.  
⚠️ This custom version is not available in Python Package Index (pyPI) yet.  
It requires your PIP environment variables to point to the local repository where it is archived. See details in [README "Install Package" section](.\README.md#install-package).

## Installing `hatch` using installer

⚠️ **This requires admin rights on your machine.**

* Download and run the installer using the standard Windows msiexec program, specifying one of the `.msi` files as the source. Use the `/passive` and `/i` parameters to request an unattended, normal installation:  
`msiexec /passive /i https://github.com/pypa/hatch/releases/latest/download/hatch-x64.msi`

## Installing `hatch` as isolated Python Package

This uses [pipx](https://pipx.pypa.io/) which allows for the global installation of Python applications in isolated environments.

* [Install](https://pipx.pypa.io/stable/installation/) `pipx`:  
`py -m pip install --user pipx`  
Once done, it is possible (even most likely) the above finishes with a WARNING looking similar to this:  
`WARNING: The script pipx.exe is installed in '<USER folder>\AppData\Roaming\Python\Python3x\Scripts' which is not on PATH`  
If so, go to the mentioned folder, allowing you to run the pipx executable directly. Enter the following line (even if you did not get the warning):  
`.\pipx.exe ensurepath`  
This adds necessary paths to your search path.  
Restart your terminal session and verify pipx does run.
* Install `hatch` using this command:  
`pipx install hatch`

&nbsp;  

___
# Build Project

When ready to build a new version of the project, proceed as followed:

* Update `__version__` variable in `__init__.py`.  
You can use [hatch version command](https://hatch.pypa.io/1.9/version/) to do it automatically:  
`hatch version [options]`

* Commit all changes, including the `__version__` update, in your repository.

* Add a tag to this commit matching `__version__`.

* Push commit & tag to the remote repository.

* Execute the build command:
   * If not standalone executable is created:  
      `hatch build` or `hatch build -t sdist -t wheel`
   * If standalone executable is to be created:
      `hatch build -t sdist -t wheel -t pyinstaller`

* 2 to 3 distribution formats are created:
   * sdist (.tar.gz archive) - *always*
   * wheel (.whl archive) - *always*
   * binaries (.exe files) - *only if building standalone executables*

&nbsp;  

___
# Publish Package

🚧 This is yet to be defined 🚧
