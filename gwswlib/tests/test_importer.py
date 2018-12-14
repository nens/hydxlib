# -*- coding: utf-8 -*-
"""Tests for importer.py"""
from gwswlib.importer import check_headers, importhydx


def test_check_headers(caplog):
    a = [1, 2, 3]
    b = [2, 3, 4]
    check_headers(a, b)
    assert "missing columns" in caplog.text
    assert "extra columns" in caplog.text


def test_check_headers_2(caplog):
    a = [1, 2, 3]
    b = [1, 2, 3]
    check_headers(a, b)
    assert "missing columns" not in caplog.text
    assert "extra columns" not in caplog.text


def test_import_knooppunt_csv_into_hydx_class():
    hydx_path = "D:\\Documents\\GitHub\\gwswlib\\gwswlib\\tests\\example_files_structures_hydx\\"
    hydx = importhydx(hydx_path)
    assert hydx.connection_nodes[1].x_coordinaat == 241318.559
