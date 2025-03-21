# -*- coding: utf-8 -*-
"""
A library for the GWSW-hydx exchange format
=============================================================================
Consists of a import and export functionality for currently hydx and threedi.
Author: Arnold van 't Veld - Nelen & Schuurmans
"""
import logging
import os
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from datetime import datetime

from .exporter import export_threedi
from .importer import import_hydx

logger = logging.getLogger(__name__)


class OptionException(Exception):
    pass


def run_import_export(hydx_path=None, out_path=None):
    """Run import and export functionality of hydxlib

    Args:
        hydx_path (str):            folder with your hydx *.csv files
        out_path (str):             output path

    Returns:
        string: "INFO: method is finished"threedi_db_settings

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

    hydx = import_hydx(hydx_path)

    export_threedi(hydx, out_path)

    logger.info("Exchange of GWSW-hydx finished")

    return "method is finished"  # Return value only for testing


def write_logging_to_file(log_relpath):
    """Add file handler for writing logfile with warning and errors of hydxlib"""
    fh = logging.FileHandler(log_relpath, mode="w")
    fh.setLevel(logging.WARNING)
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    logging.getLogger("hydxlib").addHandler(fh)
    return


def get_parser():
    """Return argument parser."""
    parser = ArgumentParser(
        description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "hydx_path",
        nargs=1,
        help="Folder with your hydx *.csv files",
    )
    parser.add_argument(
        "out_path",
        nargs=1,
        help="Output path",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        default=False,
        help="Verbose output",
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
    log_relpath = os.path.join(
        os.path.abspath(options.hydx_path[0]), "import_hydx_hydxlib.log"
    )
    write_logging_to_file(log_relpath)
    logger.info("Log file is created in hydx directory: %r", log_relpath)

    try:
        run_import_export(
            options.export_type,
            options.hydx_path[0],
            options.out_path[0],
        )
    except OptionException as e:
        logger.critical(e)
        sys.exit(1)
