# -*- coding: utf-8 -*-
"""
A library for the GWSW-hydx exchange format
=============================================================================
Consists of a import and export functionality for currently hydx and threedi.
Author: Arnold van 't Veld - Nelen & Schuurmans
"""
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import logging
import os
import sys
from datetime import datetime

from gwswlib.importer import import_hydx
from gwswlib.exporter import export_threedi

logger = logging.getLogger(__name__)


if "TRAVIS" in os.environ:
    # TODO: temporary measure, Reinout will have to investigate proper db env
    # variables. If we run on travis-ci, the default password should be empty.
    TODO_TREEDI_DB_PASSWORD = ""
else:
    TODO_TREEDI_DB_PASSWORD = "postgres"


class OptionException(Exception):
    pass


def run_import_export(
    import_type, export_type, hydx_path=None, threedi_db_settings=None
):
    logger.info("Started exchange of GWSW-hydx at %s", datetime.now())
    logger.info("import type: %s ", import_type)
    logger.info("export type: %s ", export_type)

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
    fh = logging.FileHandler(log_relpath, mode="w")
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    logging.getLogger("").addHandler(fh)


def get_parser():
    """ Return argument parser. """
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
        choices=["hydx", "threedi"],
        help="select your import operator",
    )
    parser.add_argument(
        "--export",
        dest="export_type",
        default="threedi",
        choices=["hydx", "threedi", "json"],
        help="select your export operator",
    )

    group_hydx = parser.add_argument_group("Import or export a hydx")
    group_hydx.add_argument(
        "--hydx_path",
        default="gwswlib\\tests\\example_files_structures_hydx",
        metavar="HYDX_PATH",
        dest="hydx_path",
        help="Folder with your hydx *.csv files",
    )
    group_threedi = parser.add_argument_group("Import or export a 3di database")
    group_threedi.add_argument(
        "--threedi_dbname",
        metavar="DBNAME",
        default="test_gwsw",
        dest="threedi_dbname",
        help="name of your threedi database",
    )
    group_threedi.add_argument(
        "--threedi_host",
        default="localhost",
        metavar="HOST",
        dest="threedi_host",
        help="host of your threedi database",
    )
    group_threedi.add_argument(
        "--threedi_user",
        default="postgres",
        metavar="USERNAME",
        dest="threedi_user",
        help="username of your threedi database",
    )
    group_threedi.add_argument(
        "--threedi_password",
        default=TODO_TREEDI_DB_PASSWORD,
        metavar="PASSWORD",
        dest="threedi_password",
        help="password of your threedi database",
    )
    group_threedi.add_argument(
        "--threedi_port",
        default=5432,
        type=int,
        metavar="PORT",
        dest="threedi_port",
        help="port of your threedi database",
    )
    return parser


def main(raw_args=None):
    """ Call command with args from parser. """
    options = get_parser().parse_args(raw_args)
    threedi_db_settings = {
        k: vars(options)[k] for k in vars(options) if k.startswith("threedi_")
    }

    if options.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

    # add file handler to logging options
    if options.import_type == "hydx":
        log_relpath = os.path.join(
            os.path.abspath(options.hydx_path), "import_hydx_gwswlib.log"
        )
        write_logging_to_file(log_relpath)
        logger.info("Log file is created in hydx directory: %r", log_relpath)

    try:
        run_import_export(
            options.import_type,
            options.export_type,
            options.hydx_path,
            threedi_db_settings,
        )
    except OptionException as e:
        logger.critical(e)
        sys.exit(1)
