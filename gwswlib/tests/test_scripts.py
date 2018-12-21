# -*- coding: utf-8 -*-
"""Tests for scripts.py"""
import mock
import pytest

from gwswlib import scripts


@mock.patch("sys.argv", ["program"])
def test_get_parser():
    parser = scripts.get_parser()
    # As a test, we just check one option. That's enough.
    options = parser.parse_args()
    assert options.verbose is False


def test_run_import_export_same(caplog):
    import_type = "hydx"
    export_type = "hydx"
    with pytest.raises(scripts.OptionException):
        scripts.run_import_export(import_type, export_type)


def test_run_import_export_not_available_import(caplog):
    import_type = "this is wrong"
    export_type = "threedi"
    with pytest.raises(scripts.OptionException):
        scripts.run_import_export(import_type, export_type)


def test_run_import_export_not_available_export(caplog):
    import_type = "hydx"
    hydx_path = "gwswlib/tests/example_files_structures_hydx/"
    export_type = "this is wrong"
    with pytest.raises(scripts.OptionException):
        scripts.run_import_export(import_type, export_type, hydx_path)
