# -*- coding: utf-8 -*-
import logging
import os
import csv

from gwswlib.hydx import Hydx

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
    connectedcsvfiles = [
        # "BOP1.csv",
        # "Debiet1.csv",
        # "GroeneDaken1.csv",
        # "ItObject1.csv",
        "Knooppunt1.csv",
        "Kunstwerk1.csv",
        # "Meta1.csv",
        # "Nwrw.csv",
        # "Oppervlak1.csv",
        # "Profiel1.csv",
        "Verbinding1.csv",
        # "Verloop1.csv",
    ]

    existing_files = []
    for f in hydxcsvfiles:
        csvpath = os.path.join(hydx_path, f)
        if not os.path.isfile(csvpath):
            logger.warning("The following hydx file could not be found: %s", csvpath)
        elif f not in connectedcsvfiles:
            logger.warning(
                "The following hydx file is currently not connected in this importer: %s",
                csvpath,
            )
        else:
            existing_files.append(f)

    # TODO check if number of csvfiles loaded is same as number inside meta1.csv

    for f in existing_files:
        csvpath = os.path.join(hydx_path, f)
        with open(csvpath) as csvfile:
            csvreader = csv.DictReader(csvfile, delimiter=";")
            check_headers(csvreader.fieldnames, Hydx.csvheaders(f))
            for line in csvreader:
                hydx.import_csvline(line, f)

    hydx.check_import_data()

    return hydx


def check_headers(found, expected):
    """Compares two header columns on extra or missing ones"""
    extra_columns = set(found) - set(expected)
    missing_columns = set(expected) - set(found)
    if extra_columns:
        logger.warning("extra columns found: %s", extra_columns)

    if missing_columns:
        logger.error("missing columns found: %s", missing_columns)
