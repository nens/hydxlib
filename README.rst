A library for the GWSW-hydx exchange format
===========================================

In de toekomst gaat RioNED het GWSW gebruiken als standaard uitwisselingsformaat voor (hydraulische) rioleringsgegevens.
Deze tool zorgt voor de uitwisseling tussen het GWSW-hyd en de 3Di database.
Voor meer informatie over GWSW-hyd zie https://apps.gwsw.nl/item_definition
Voor meer informatie over het databaseschema van 3Di zie https://docs.3di.lizard.net/en/stable/d_before_you_begin.html#database-overview

Purporse of this script is to exchange information between different formats.
This means that this library doesn't improve lacking or incorrect data.
For example, it doesn't remove double manholes on the same location.
This libary does provide all kinds of checks with warning and error messages.


Installation
------------

We're installed with `pipenv <https://docs.pipenv.org/>`_, a handy wrapper
around pip and virtualenv. Install that first with ``pip install
pipenv``. Then run::

  $ PIPENV_VENV_IN_PROJECT=1 pipenv --three
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


Development version
-------------------

The following objects will be supported

* Structures

  * Pumpstations

  * Weirs

  * Orifices


Current assumptions or shortages
--------------------------------

Ideas for structure code: https://github.com/nens/ribxlib

Running script
--------------

**Export**

Input: 3Di database with sewerage system

Output: GWSW-hyd in CSV-format

**Import**

Input: GWSW-hyd in CSV-format

Output: 3Di database with sewerage system