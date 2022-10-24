# -*- coding: utf-8 -*-
"""Tests for scripts.py"""
from hydxlib import scripts

import mock
import pytest


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
    hydx_path = "hydxlib/tests/example_files_structures_hydx/"
    export_type = "this is wrong"
    with pytest.raises(scripts.OptionException):
        scripts.run_import_export(import_type, export_type, hydx_path)


def test_run_import_export_log_file(caplog, mock_exporter_db):
    import_type = "hydx"
    hydx_path = "hydxlib/tests/example_files_structures_hydx/"
    export_type = "threedi"
    finished = scripts.run_import_export(
        import_type, export_type, hydx_path, "/some/path"
    )
    assert finished == "method is finished"
