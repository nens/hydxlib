GWSW-Hyd import and export voor 3Di
===================================
In de toekomst gaat RioNED het GWSW gebruiken als standaard uitwisselingsformaat voor (hydraulische) rioleringsgegevens.
Deze tool zorgt voor de uitwisseling tussen het GWSW-hyd en de 3Di database.
Voor meer informatie over GWSW-hyd zie https://apps.gwsw.nl/item_definition
Voor meer informatie over het databaseschema van 3Di zie https://docs.3di.lizard.net/en/stable/d_before_you_begin.html#database-overview

Development version
-------------------
The following objects will be supported
* Structures
** Pumpstations
** Weirs
** Orifices

Current assumptions or shortages
--------------------------------


Running script
--------------
**Export**
Input: 3Di database with sewerage system
Output: GWSW-hyd in CSV-format

**Import**
Input: GWSW-hyd in CSV-format
Output: 3Di database with sewerage system

Installation::

    $ PIPENV_VENV_IN_PROJECT=1 pipenv --three
    $ pipenv install