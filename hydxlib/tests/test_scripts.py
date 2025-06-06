# -*- coding: utf-8 -*-
"""Tests for scripts.py"""
from unittest import mock

from hydxlib import scripts


@mock.patch("sys.argv", ["program", "a", "b"])
def test_get_parser():
    parser = scripts.get_parser()
    options = parser.parse_args()
    assert options.verbose is False
    assert options.hydx_path[0] == "a"
    assert options.out_path[0] == "b"


def test_run_import_export_log_file(mock_exporter_db):
    hydx_path = "hydxlib/tests/example_files_structures_hydx/"
    finished = scripts.run_import_export(hydx_path, "/some/path")
    assert finished == "method is finished"
