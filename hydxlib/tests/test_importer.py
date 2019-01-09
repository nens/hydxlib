# -*- coding: utf-8 -*-
"""Tests for importer.py"""
from hydxlib.importer import import_hydx


def test_import_connection_node_csv_into_hydx_class():
    hydx_path = "hydxlib/tests/example_files_structures_hydx/"
    hydx = import_hydx(hydx_path)
    assert hydx.connection_nodes[1].x_coordinaat == 241318.559


def test_import_connection_csv_into_hydx_class():
    hydx_path = "hydxlib/tests/example_files_structures_hydx/"
    hydx = import_hydx(hydx_path)
    assert hydx.connections[6].identificatieknooppuntofverbinding == "ovs2"


def test_import_structure_csv_into_hydx_class():
    hydx_path = "hydxlib/tests/example_files_structures_hydx/"
    hydx = import_hydx(hydx_path)
    assert hydx.structures[7].identificatieknooppuntofverbinding == "drl1"


def test_import_profile_csv_into_hydx_class():
    hydx_path = "hydxlib/tests/example_files_structures_hydx/"
    hydx = import_hydx(hydx_path)
    assert hydx.profiles[99].breedte_diameterprofiel == "355"
