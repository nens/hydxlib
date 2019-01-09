# -*- coding: utf-8 -*-
import logging
import os
import csv

from hydxlib.hydx import Hydx

logger = logging.getLogger(__name__)


def import_hydx(hydx_path):
    """Read set of hydx-csvfiles and return Hydx objects"""
    hydx = Hydx()

    hydxcsvfiles = [
        "BOP1.csv",
        "Debiet1.csv",
        "GroeneDaken1.csv",
        "ItObject1.csv",
        "Knooppunt1.csv",
        "Kunstwerk1.csv",
        "Meta1.csv",
        "Nwrw.csv",
        "Oppervlak1.csv",
        "Profiel1.csv",
        "Verbinding1.csv",
        "Verloop1.csv",
    ]
    implementedcsvfiles = [
        # "BOP1.csv",
        # "Debiet1.csv",
        # "GroeneDaken1.csv",
        # "ItObject1.csv",
        "Knooppunt1.csv",
        "Kunstwerk1.csv",
        # "Meta1.csv",
        # "Nwrw.csv",
        # "Oppervlak1.csv",
        "Profiel1.csv",
        "Verbinding1.csv",
        # "Verloop1.csv",
    ]

    existing_files = []
    for f in hydxcsvfiles:
        csvpath = os.path.join(hydx_path, f)
        if not os.path.isfile(csvpath):
            logger.warning(
                "The following hydx file could not be found: %s",
                os.path.abspath(csvpath),
            )
        elif f not in implementedcsvfiles:
            logger.warning(
                "The following hydx file is currently not implemented in this importer: %s",
                csvpath,
            )
        else:
            existing_files.append(f)

    # TODO check if number of csvfiles loaded is same as number inside meta1.csv

    for f in existing_files:
        csvpath = os.path.join(hydx_path, f)
        with open(csvpath) as csvfile:
            csvreader = csv.DictReader(csvfile, delimiter=";")
            hydx.import_csvfile(csvreader, f)

    hydx.check_import_data()

    return hydx
