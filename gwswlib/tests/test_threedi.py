# -*- coding: utf-8 -*-
"""Tests for threedi.py"""
from unittest import TestCase
import pytest
import mock

from gwswlib.importer import import_hydx
from gwswlib.threedi import Threedi, check_if_element_is_created_with_same_code
from gwswlib.sql_models.constants import Constants


def test_get_mapping_value_wrong(caplog):
    MANHOLE_SHAPE_MAPPING = {
        "RND": Constants.MANHOLE_SHAPE_ROUND,
        "RHK": Constants.MANHOLE_SHAPE_RECTANGLE,
    }
    shape_code = "SQR"
    record_code = "01_TEST"
    threedi = Threedi()
    threedi.get_mapping_value(
        MANHOLE_SHAPE_MAPPING, shape_code, record_code, name_for_logging="manhole shape"
    )
    assert "Unknown" in caplog.text


def test_get_mapping_value_right(caplog):
    MANHOLE_SHAPE_MAPPING = {
        "RND": Constants.MANHOLE_SHAPE_ROUND,
        "RHK": Constants.MANHOLE_SHAPE_RECTANGLE,
    }
    shape_code = "RND"
    record_code = "01_TEST"
    threedi = Threedi()
    shape = threedi.get_mapping_value(
        MANHOLE_SHAPE_MAPPING, shape_code, record_code, name_for_logging="manhole shape"
    )
    assert shape == "rnd"


def test_check_if_element_created_is_with_same_code(caplog):
    checked_element = "knp6"
    created_elements = [
        {
            "code": "knp1",
            "initial_waterlevel": None,
            "geom": (241330.836, 483540.234, 28992),
        },
        {
            "code": "knp6",
            "initial_waterlevel": None,
            "geom": (241463.858, 483356.833, 28992),
        },
    ]
    element_type = "Connection node"
    check_if_element_is_created_with_same_code(
        checked_element, created_elements, element_type
    )
    assert "Multiple elements 'Connection node' are created" in caplog.text


def test_import_hydx_unknown_connection_types(caplog):
    hydx = mock.Mock()
    hydx.connection_nodes = []
    hydx.connections = [
        mock.Mock(identificatieknooppuntofverbinding="ovs1", typeverbinding="XXX")
    ]
    threedi = Threedi()
    threedi.import_hydx(hydx)
    assert '"typeverbinding" is not recognized' in caplog.text


def test_import_hydx_known_pipe_connection(caplog):
    hydx = mock.Mock()
    hydx.connection_nodes = []
    hydx.connections = [
        mock.Mock(identificatieknooppuntofverbinding="ovs1", typeverbinding="GSL")
    ]
    threedi = Threedi()
    threedi.import_hydx(hydx)
    assert '"typeverbinding" is not implemented' in caplog.text


class TestThreedi(TestCase):
    def setUp(self):
        self.threedi = Threedi()
        hydx_path = "gwswlib/tests/example_files_structures_hydx/"
        self.hydx = import_hydx(hydx_path)

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    def test_import_hydx(self):
        self.threedi.import_hydx(self.hydx)
        assert len(self.threedi.connection_nodes) == 7

    def test_add_connection_node(self):
        connection_node_0 = {
            "code": "knp1",
            "initial_waterlevel": None,
            "geom": (241330.836, 483540.234, 28992),
        }
        self.threedi.import_hydx(self.hydx)
        # select first manhole from dataset for check
        connection_node = self.hydx.connection_nodes[0]
        self.threedi.add_connection_node(connection_node)
        assert self.threedi.connection_nodes[0] == connection_node_0

    def test_add_connection_node_manhole(self):
        manhole_0 = {
            "code": "knp1",
            "display_name": "13_990100",
            "surface_level": None,
            "width": None,
            "length": None,
            "shape": None,
            "bottom_level": None,
            "calculation_type": None,
            "manhole_indicator": 0,
        }
        self.threedi.import_hydx(self.hydx)
        # select first manhole from dataset for check
        connection_node = self.hydx.connection_nodes[0]
        self.threedi.add_connection_node(connection_node)
        assert self.threedi.manholes[0] == manhole_0
