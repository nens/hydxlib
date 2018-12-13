# -*- coding: utf-8 -*-
import logging
import os
import csv

from gwswlib.hydx import Hydx, ConnectionNode

logger = logging.getLogger(__name__)


def importhydx(hydxpath):
    """Read set of hydx-csvfiles and return Hydx objects"""
    print("hoi")

    hydx = Hydx()

    # check if hydx exists
    csvpath_knooppunt = os.path.join(hydxpath, "Knooppunt1.csv")
    if not os.path.isfile(csvpath_knooppunt):
        hint = "[!] ERROR : The specified file could not be found: "
        print(hint, csvpath_knooppunt)
        return 1

    # read knooppunt.csv (as dict)
    with open(csvpath_knooppunt) as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=";")

        # headercheck
        check_headers(csvreader.fieldnames, ConnectionNode.csvheaders())

        # read csv line by line
        for line in csvreader:
            print(dict(line))
            connection_node = ConnectionNode(codes=line)
            hydx.connection_nodes.append(connection_node)

    # read csvlines etc

    #
    return hydx


def check_headers(found, expected):
    """Read set of hydx-csvfiles and return Hydx objects"""
    extra_columns = set(found) - set(expected)
    missing_columns = set(expected) - set(found)
    if extra_columns:
        logger.warning("extra columns found: %s", extra_columns)

    if missing_columns:
        logger.error("missing columns found: %s", missing_columns)


def importthreedi(database, hydxdict):
    print("hoi")
