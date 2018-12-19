# -*- coding: utf-8 -*-
"""Tests for hydx.py"""
from collections import OrderedDict
from unittest import TestCase
import pytest

from gwswlib.hydx import ConnectionNode
from gwswlib.importer import import_hydx


def test_touch_csvheaders():
    csvheaders = ConnectionNode.csvheaders()
    assert "INI_NIV" in csvheaders


def test_check_init_connectionnode():
    line_in = OrderedDict(
        [
            ("UNI_IDE", "knp1"),
            ("RST_IDE", "GEMENGD-13 Nijrees"),
            ("PUT_IDE", "13_990100"),
            ("KNP_XCO", "241330.836"),
            ("KNP_YCO", "483540.234"),
            ("CMP_IDE", ""),
            ("MVD_NIV", ""),
            ("MVD_SCH", ""),
            ("WOS_OPP", ""),
            ("KNP_MAT", ""),
            ("KNP_VRM", ""),
            ("KNP_BOK", ""),
            ("KNP_BRE", ""),
            ("KNP_LEN", ""),
            ("KNP_TYP", "INS"),
            ("INI_NIV", ""),
            ("STA_OBJ", ""),
            ("AAN_MVD", ""),
            ("ITO_IDE", ""),
            ("ALG_TOE", ""),
        ]
    )
    line_out = {
        "identificatieknooppuntofverbinding": "knp1",
        "identificatierioolstelsel": "GEMENGD-13 Nijrees",
        "identificatierioolput": "13_990100",
        "x_coordinaat": 241330.836,
        "y_coordinaat": 483540.234,
        "identificatiecompartiment": None,
        "niveaumaaiveld": None,
        "maaiveldschematisering": None,
        "oppervlakwateropstraat": None,
        "materiaalput": None,
        "vormput": None,
        "niveaubinnenonderkantput": None,
        "breedte_diameterputbodem": None,
        "lengteputbodem": None,
        "typeknooppunt": "INS",
        "initielewaterstand": None,
        "statusobject": None,
        "aannamemaaiveldhoogte": None,
        "identificatiedefinitieit_object": None,
        "toelichtingregel": None,
    }
    connection_node = ConnectionNode()
    connection_node.import_csvline(csvline=line_in)
    assert connection_node.__dict__ == line_out


def test_repr_connection_nodes():
    connection_node = ConnectionNode()
    assert repr(connection_node)


class TestHydx(TestCase):
    def setUp(self):
        hydx_path = "gwswlib/tests/example_files_structures_hydx/"
        self.hydx = import_hydx(hydx_path)

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    def test_check_on_unique(self):
        self.hydx._check_on_unique(
            self.hydx.connection_nodes, "identificatieknooppuntofverbinding"
        )
        assert "double" in self._caplog.text
