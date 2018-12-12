# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)


def importhydx(csvfile):
    """Read set of hydx-csvfiles and return Hydx objects"""
    print("hoi")

    hydx = Hydx()
    # read knooppunt.csv (as dict)

    # headercheck
    check_headers(found, ConnectionNode.csvheaders)
    #
    for line in csv:
        connection_node = ConnectionNode(codes=line)
        hydx.connection_nodes.append(connection_node)

    # read csvlines etc

    #
    return hydx


def check_headers(found, expected):
    """Read set of hydx-csvfiles and return Hydx objects"""


def importthreedi(database, hydxdict):
    print("hoi")
