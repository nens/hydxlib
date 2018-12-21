# -*- coding: utf-8 -*-
import logging
import os
import csv

from gwswlib.hydx import Hydx, ConnectionNode, Connection

logger = logging.getLogger(__name__)


def import_hydx(hydx_path):
    """Read set of hydx-csvfiles and return Hydx objects"""
    hydx = Hydx()
    csvfiles = [
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

    # check if csv file exists
    for f in csvfiles:
        csvpath = os.path.join(hydx_path, f)
        if not os.path.isfile(csvpath):
            logger.warning("The following hydx file could not be found: %s", csvpath)

    csvpath_knooppunt = os.path.join(hydx_path, "Knooppunt1.csv")
    # read knooppunt.csv (as dict)
    with open(csvpath_knooppunt) as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=";")

        check_headers(csvreader.fieldnames, ConnectionNode.csvheaders())

        for line in csvreader:
            connection_node = ConnectionNode()
            connection_node.import_csvline(csvline=line)
            hydx.connection_nodes.append(connection_node)

    csvpath_knooppunt = os.path.join(hydx_path, "Verbinding1.csv")
    # read knooppunt.csv (as dict)
    with open(csvpath_knooppunt) as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=";")

        check_headers(csvreader.fieldnames, Connection.csvheaders())

        for line in csvreader:
            connection = Connection()
            print(line)
            connection.import_csvline(csvline=line)
            print(connection.__dict__)
            hydx.connections.append(connection)

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
