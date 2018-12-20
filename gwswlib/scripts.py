# -*- coding: utf-8 -*-
"""
A library for the GWSW-hydx exchange format
=============================================================================
Consists of a import and export functionality for currently hydx and threedi.
Author: Arnold van 't Veld - Nelen & Schuurmans
"""
from argparse import ArgumentParser, RawTextHelpFormatter
import logging

from gwswlib.importer import import_hydx
from gwswlib.exporter import export_threedi

logger = logging.getLogger(__name__)


def get_parser():
    """ Return argument parser. """
    parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        default=False,
        help="Verbose output",
    )
    parser.add_argument(
        "--import",
        dest="import_type",
        default="hydx",
        metavar="import_type (hydx or threedi)",
        choices=["hydx", "threedi"],
        help="select your import operator:\n hydx (default) or threedi (not implemented)",
    )
    parser.add_argument(
        "--export",
        dest="export_type",
        default="threedi",
        metavar="export_type (hydx, threedi or json)",
        choices=["hydx", "threedi", "json"],
        help="select your import operator:\n hydx (not implemented), threedi or json (not implemented)",
    )

    group_import_hydx = parser.add_argument_group("Import or export a hydx")
    group_import_hydx.add_argument(
        "--hydx_path",
        default="gwswlib\\tests\\example_files_structures_hydx",
        metavar="hydx_path",
        dest="hydx_path",
        help='Folder with your hydx *.csv files\n\
            (example: "gwswlib\\tests\\example_files_structures_hydx\\")',
    )
    group_threedi = parser.add_argument_group("Import or export a 3di database")
    group_threedi.add_argument(
        "--threedi_dbname",
        metavar="dbname",
        default="test_gwsw",
        dest="threedi_dbname",
        help="name of your threedi database\n (example: 'test_gwsw')",
    )
    group_threedi.add_argument(
        "--threedi_host",
        default="localhost",
        metavar="host",
        dest="threedi_host",
        help="host of your threedi database\n (default: 'localhost')",
    )
    group_threedi.add_argument(
        "--threedi_user",
        default="postgres",
        metavar="username",
        dest="threedi_user",
        help="username of your threedi database\n (default: 'postgres')",
    )
    group_threedi.add_argument(
        "--threedi_password",
        default="postgres",
        metavar="password",
        dest="threedi_password",
        help="password of your threedi database\n (default: 'postgres')",
    )
    group_threedi.add_argument(
        "--threedi_port",
        default=5432,
        type=int,
        metavar="port",
        dest="threedi_port",
        help="port of your threedi database\n (default: '5432')",
    )
    return parser


def main():
    """ Call command with args from parser. """
    options = get_parser().parse_args()
    threedi_db_settings = {
        k: vars(options)[k] for k in vars(options) if k.startswith("threedi_")
    }

    if options.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

    if options.import_type == "hydx":
        hydx = import_hydx(options.hydx_path)
    # TODO volgens mij is deze niet nodig, omdat de parser al opties heeft
    else:
        logging.warning("no available import type is selected")
        raise

    if options.export_type == "threedi":
        export_threedi(hydx, threedi_db_settings)
    # TODO volgens mij is deze niet nodig, omdat de parser al opties heeft
    else:
        logging.warning("no available export type is selected")
        raise
    