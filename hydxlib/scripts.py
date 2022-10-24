# -*- coding: utf-8 -*-
"""
A library for the GWSW-hydx exchange format
=============================================================================
Consists of a import and export functionality for currently hydx and threedi.
Author: Arnold van 't Veld - Nelen & Schuurmans
"""
from .exporter import export_threedi
from .importer import import_hydx
from argparse import ArgumentDefaultsHelpFormatter
from argparse import ArgumentParser
from datetime import datetime

import logging
import os
import sys


logger = logging.getLogger(__name__)


class OptionException(Exception):
    pass


def run_import_export(
    import_type, export_type, hydx_path=None, threedi_db_settings=None
):
    """Run import and export functionality of hydxlib

    Args:
        import_type (str):          import operator ["hydx", "threedi"]
        export_type (str):          export operator ["hydx", "threedi", "json"]
        hydx_path (str):            folder with your hydx *.csv files
        threedi_db_settings (str):  path to the 3Di spatialite file

    Returns:
        string: "INFO: method is finished"

    *import_type*
        hydx
        threedi (not yet supported)

    *export_type*
        hydx (not yet supported)
        threedi
        json (not yet supported)

    *hydx_path*
        required when selected operator 'hydx'

        relative or absolute path to your hydx location files
        example: hydx_path = "hydxlib\\tests\\example_files_structures_hydx"

    *threedi_db_settings*
        required when selected operator 'threedi'

        a path to a spatialite file

    usage example:
        from hydxlib import run_import_export, write_logging_to_file
        log_relpath = log_relpath = os.path.join(
            os.path.abspath(options.hydx_path), "import_hydx_hydxlib.log"
        )
        write_logging_to_file(hydx_path)
        run_import_export(import_type, export_type, hydx_path, threedi_db_settings)

    """
    logger.info("Started exchange of GWSW-hydx at %s", datetime.now())
    logger.info("import type %r ", import_type)
    logger.info("export type %r ", export_type)

    if import_type == export_type:
        raise OptionException(
            "not allowed to use same import and export type %r" % import_type
        )

    if import_type == "hydx":
        hydx = import_hydx(hydx_path)
    else:
        raise OptionException("no available import type %r is selected" % import_type)

    if export_type == "threedi":
        export_threedi(hydx, threedi_db_settings)
    else:
        raise OptionException("no available export type %r is selected" % export_type)

    logger.info("Exchange of GWSW-hydx finished")

    return "method is finished"  # Return value only for testing


def write_logging_to_file(log_relpath):
    """Add file handler for writing logfile with warning and errors of hydxlib"""
    fh = logging.FileHandler(log_relpath, mode="w")
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    logging.getLogger("import_hydx").addHandler(fh)
    return


def get_parser():
    """Return argument parser."""
    parser = ArgumentParser(
        description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter
    )
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
        choices=["hydx"],
        help="select your import operator",
    )
    parser.add_argument(
        "--export",
        dest="export_type",
        default="threedi",
        choices=["threedi"],
        help="select your export operator",
    )

    group_hydx = parser.add_argument_group("Import or export a hydx")
    group_hydx.add_argument(
        "--hydx_path",
        metavar="HYDX_PATH",
        dest="hydx_path",
        help="Folder with your hydx *.csv files",
        required=True,
    )
    group_threedi = parser.add_argument_group("Import or export a 3di database")
    group_threedi.add_argument(
        "--sqlite_path",
        metavar="SQLITE_PATH",
        dest="sqlite_path",
        help="Path to your 3Di *.sqlite file",
        required=True,
    )
    return parser


def main():
    """Call command with args from parser."""
    options = get_parser().parse_args()

    if options.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

    # add file handler to logging options
    if options.import_type == "hydx":
        log_relpath = os.path.join(
            os.path.abspath(options.hydx_path), "import_hydx_hydxlib.log"
        )
        write_logging_to_file(log_relpath)
        logger.info("Log file is created in hydx directory: %r", log_relpath)

    try:
        run_import_export(
            options.import_type,
            options.export_type,
            options.hydx_path,
            options.sqlite_path,
        )
    except OptionException as e:
        logger.critical(e)
        sys.exit(1)
