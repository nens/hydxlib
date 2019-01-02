# -*- coding: utf-8 -*-
"""Tests for importer.py"""
from gwswlib.importer import import_hydx


def test_import_connection_node_csv_into_hydx_class():
    hydx_path = "gwswlib/tests/example_files_structures_hydx/"
    hydx = import_hydx(hydx_path)
    assert hydx.connection_nodes[1].x_coordinaat == 241318.559


def test_import_connection_csv_into_hydx_class():
    hydx_path = "gwswlib/tests/example_files_structures_hydx/"
    hydx = import_hydx(hydx_path)
    assert hydx.connections[4].identificatieknooppuntofverbinding == "ovs2"
