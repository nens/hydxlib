# -*- coding: utf-8 -*-
"""Tests for importer.py"""
from hydxlib.importer import import_hydx

import logging


def test_import_profile_csv_into_hydx_class(hydx, caplog):
    caplog.set_level(logging.ERROR)
    hydx_path = "hydxlib/tests/example_files_structures_hydx/"
    hydx = import_hydx(hydx_path)
    assert hydx.connection_nodes[1].x_coordinaat == 300
    assert hydx.connections[6].identificatieknooppuntofverbinding == "lei13"
    assert hydx.structures[7].identificatieknooppuntofverbinding == "ovs84"
    assert hydx.profiles[37].breedte_diameterprofiel == "400"
    assert len(caplog.records) == 1
    assert (
        caplog.records[0].message
        == "Non-unique 'identificatieknooppuntofverbinding' value encountered in Knooppunt knp9"
    )
