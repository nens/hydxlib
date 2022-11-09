# -*- coding: utf-8 -*-
"""Tests for scripts.py"""
from hydxlib import scripts
from unittest import mock


@mock.patch("sys.argv", ["program", "a", "b"])
def test_get_parser():
    parser = scripts.get_parser()
    options = parser.parse_args()
    assert options.verbose is False
    assert options.export_type == "threedi"
    assert options.hydx_path[0] == "a"
    assert options.out_path[0] == "b"


def test_run_import_export_log_file(mock_exporter_db):
    hydx_path = "hydxlib/tests/example_files_structures_hydx/"
    export_type = "threedi"
    finished = scripts.run_import_export(export_type, hydx_path, "/some/path")
    assert finished == "method is finished"
