# -*- coding: utf-8 -*-
"""TODO Docstring, used in the command line help text."""
import argparse
import logging

from gwswlib.importer import importhydx

logger = logging.getLogger(__name__)


def get_parser():
    """ Return argument parser. """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        default=False,
        help="Verbose output",
    )
    parser.add_argument(
        "--hydx",
        default=None,
        metavar="hydxpath",
        dest="hydxpath",
        help="Set folder to your hydx csvfiles",
    )
    return parser


def main():
    """ Call command with args from parser. """
    options = get_parser().parse_args()
    if options.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

    try:
        importhydx(options.hydxpath)
    except Exception:
        logger.exception("An exception has occurred.")
        return 1


if __name__ == "__main__":
    exit(main())
