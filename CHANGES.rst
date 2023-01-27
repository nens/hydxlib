Changelog of hydxlib
===================================================


1.4 (2023-01-27)
----------------

- Added threedi-schema as a dependency, removing threedi-modelchecker

- Fixed writing logging to file


1.3 (2022-12-12)
----------------

- Fixed all tabulated profiles (TAB, HEU, MVR, UVR, OVA) and added TPZ and YZP.

- Added inverted egg (EIG) profile.

- Added trapezium profile in case no tabulated profile is given.

- Add all cross sections to the 3Di spatialite and use the identifications from the
  input file.

- Check if a profile is open/closed depending on the verbinding type (OPL or not).


1.2 (2022-12-06)
----------------

- Added Heul (HEU), U-Vorm (UVR), Ovaal (OVA) profielen, fixed Muil (MVR),
  removed trapezium (TPZ).

- Fixed empty connection_node.the_geom column.


1.1 (2022-11-09)
----------------

- Log through the hydxlib.* logger instead of the root logger.

- Emit error log if a value is required according to GWSW, but missing.

- Made log messages more comprehensible by using terminology from GWSW instead
  of internal model and field names.

- Set KNP_MAT to not required.

- Emit more comprehensible error if a verbinding with types GSL, OPL, ITR,
  or DRL has no profile.


1.0 (2022-10-25)
----------------

- Backport changes from https://github.com/threedi/beta-plugins.

- Added threedi-modelchecker as a dependency, and used the 3Di schema in
  it as a replacement for hydxlib.sql_models.

- Removed PostGRES support (only spatialite remains).

- Replaced GDAL with pyproj.

- An 'RHK' profile is now interpreted as a closed (instead of open) rectangle.

- Add JSON export format.


0.7 (2020-03-03)
----------------

- Closing database connection
- Updating bug in rectangular cross sections


0.6 (2019-11-22)
----------------

- Using the final version of the hydx format.


0.5 (2019-02-12)
----------------

- Bug fix discharge coefficient orifices in Threedi.


0.4 (2019-01-18)
----------------

- Small fixes.


0.3 (2019-01-09)
----------------

- Added docstrings and updated the readme.


0.2 (2019-01-09)
----------------

- Enabled automatic pypi.org uploads from travis-ci.com


0.1 (2019-01-09)
----------------

- Initial project structure created with cookiecutter and
  https://github.com/nens/cookiecutter-python-template .

- Set up automatic testing with travis: https://travis-ci.com/nens/hydxlib .

- First working version with hydx import and 3Di postgres output.
  In this version only nodes, weirs, orifices and pumpstations are supported.
