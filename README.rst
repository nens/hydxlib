A library for the GWSW-hydx exchange format
===========================================

RioNED is going to release a new format for exchanging sewerage data called GWSW-hydx.
This tool could be used to exchange sewerage data from and to a hydx format (``*.csv``).

For more information about GWSW-hydx:
https://apps.gwsw.nl/item_definition

For more information about the database scheme of 3Di:
https://docs.3di.lizard.net/en/stable/d_before_you_begin.html#database-overview

Purporse of this script is to exchange information between different formats.
This means that this library doesn't improve lacking or incorrect data.
For example, it doesn't remove double manholes on the same location.
This libary does provide all kinds of checks with warning and error messages.

This tool is currently in development.
Therefore only nodes, weirs, orifices and pumpstations are currently supported.


Installation
------------

We're installed with::

  $ pip install hydxlib


Running script
--------------

It's possible to run this tool on command line or with python

Commandline::

  $ hydxlib --import_type hydx --export_type threedi etc.

Python::

  from hydxlib import run_import_export, write_logging_to_file

  log_relpath = os.path.join(os.path.abspath(options.hydx_path),
                             "import_hydx_hydxlib.log")
  write_logging_to_file(hydx_path)
  run_import_export(import_type, export_type, hydx_path, threedi_db_settings)


Installation for development
----------------------------

We're installed with `pipenv <https://docs.pipenv.org/>`_, a handy wrapper
around pip and virtualenv. Install that first with ``pip install
pipenv``. Then run on Linux::

  $ PIPENV_VENV_IN_PROJECT=1 pipenv --three
  $ pipenv install --dev

on Windows::

  $ set PIPENV_VENV_IN_PROJECT=1
  $ pipenv --three
  $ pipenv install --dev

There will be a script you can run like this::

  $ pipenv run run-hydxlib

It runs the `main()` function in `hydxlib/scripts.py`,
adjust that if necessary. The script is configured in `setup.py` (see
`entry_points`).

In order to get nicely formatted python files without having to spend manual
work on it, run the following command periodically::

  $ pipenv run black hydxlib

Run the tests regularly. This also checks with pyflakes, black and it reports
coverage. Pure luxury::

  $ pipenv run pytest

The tests are also run automatically on "travis", you'll see it in the pull
requests. There's also `coverage reporting
<https://coveralls.io/github/nens/hydxlib>`_ on coveralls.io.
