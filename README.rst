A library for the GWSW-hydx exchange format
===========================================

RioNED is going to release a new format for exchanging sewerage data called GWSW-hydx.
hydxlib can be used to import sewerage data from a hydx format (``*.csv``) to
3Di native spatialite files, or alternatively JSON.

For more information about GWSW-hydx:
https://apps.gwsw.nl/item_hyddef

For more information about the database scheme of 3Di:
https://docs.3di.live/

Purporse of this script is to exchange information between different formats.
This means that this library doesn't improve lacking or incorrect data.
For example, it doesn't remove double manholes on the same location.
This libary does provide all kinds of checks with warning and error messages.

This tool is currently in development.
Therefore only nodes, weirs, orifices and pumpstations are currently supported.


Installation
------------

hydxlib is installed with::

  $ pip install hydxlib


Running script
--------------

It's possible to run this tool on command line or with python.

Commandline::

  $ run-hydxlib path/to/hydx/dir path/to/threedi.sqlite

Python::

  from hydxlib import run_import_export

  run_import_export("threedi", "path/to/hydx/dir", "path/to/threedi.sqlite")


Installation for development
----------------------------

Clone ``hydxlib`` from github and then install locally using pip + virtualenv::

  $ virtualenv .venv
  $ source .venv/bin/activate
  $ pip install -e .[test]

There will be a script you can run like this::

  $ run-hydxlib ...

It runs the `main()` function in `hydxlib/scripts.py`,
adjust that if necessary. The script is configured in `setup.py` (see
`entry_points`).

Run the tests regularly::

  $ pytest hydxlib --cov

The code is linted automatically on each PR. To enable autoformatting locally,
install `pre-commit`::

  $ pre-commit install
