# -*- coding: utf-8 -*-
"""Tests for threedi.py"""
from unittest import TestCase
import pytest
import mock

from hydxlib.importer import import_hydx
from hydxlib.threedi import (
    Threedi,
    check_if_element_is_created_with_same_code,
    get_hydx_default_profile,
)
from hydxlib.sql_models.constants import Constants


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
    hydx.profiles = []
    hydx.connections = [
        mock.Mock(identificatieknooppuntofverbinding="ovs1", typeverbinding="GSL")
    ]
    threedi = Threedi()
    threedi.import_hydx(hydx)
    assert '"typeverbinding" is not implemented' in caplog.text


def test_structure_does_not_exist_error(caplog):
    hydx = mock.Mock()
    hydx.structures = []
    hydx.connection_nodes = []
    hydx.connections = [
        mock.Mock(identificatieknooppuntofverbinding="pmp1", typeverbinding="PMP")
    ]
    threedi = Threedi()
    threedi.import_hydx(hydx)
    assert "Structure does not exist for connection" in caplog.text


def test_get_hydx_default_profile():
    profile = get_hydx_default_profile()
    assert profile.breedte_diameterprofiel == "1000"


class TestThreedi(TestCase):
    def setUp(self):
        self.threedi = Threedi()
        hydx_path = "hydxlib/tests/example_files_structures_hydx/"
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
        assert self.threedi.manholes[0] == manhole_0

    def test_add_pumpstation(self):
        pumpstation_1 = {
            "code": "pmp2",
            # check if connection number 2 is created for second structure with these nodes
            "display_name": "13_990430-13_990420-2",
            "start_node.code": "knp3",
            "end_node.code": "knp4",
            "type_": 1,
            "start_level": 7.57,
            "lower_stop_level": 7.33,
            "upper_stop_level": None,
            "capacity": 18.05556,
            "sewerage": True,
        }
        self.threedi.import_hydx(self.hydx)
        assert self.threedi.pumpstations[1] == pumpstation_1

    def test_add_first_pump_with_same_code(self):
        self.threedi.import_hydx(self.hydx)
        # select first manhole from dataset for check
        connection = self.hydx.connections[0]
        structure = self.hydx.structures[0]
        self.threedi.add_structure(connection, structure)
        assert "Only first structure" in self._caplog.text

    def test_add_pump_type_2(self):
        self.threedi.import_hydx(self.hydx)
        # select first manhole from dataset for check
        connection = self.hydx.connections[0]
        structure = self.hydx.structures[0]
        self.threedi.add_structure(connection, structure)
        assert self.threedi.pumpstations[3]["type_"] == 2

    def test_add_weir_with_boundary_and_open_rectangle_profile(self):
        weir_0 = {
            "code": "ovs1",
            "display_name": "13_990100-13_990105-1",
            "start_node.code": "knp1",
            "end_node.code": "knp2",
            "cross_section_details": {
                "code": "rectangle_w1.5_open",
                "shape": 1,
                "width": 1.5,
                "height": None,
            },
            "crest_type": 4,
            "crest_level": 9.5,
            "discharge_coefficient_positive": 0.8,
            "discharge_coefficient_negative": 0.8,
            "sewerage": True,
            "boundary_details": {"timeseries": "0,9.5\n9999,9.5 ", "boundary_type": 1},
            "cross_section_code": "rectangle_w1.5_open",
        }
        self.threedi.import_hydx(self.hydx)
        assert self.threedi.weirs[0] == weir_0

    def test_add_orifice_with_rectangular_closed_profile(self):
        orifice_3 = {
            "code": "drl4",
            "display_name": "13_990560-13_990821-6",
            "start_node.code": "knp5",
            "end_node.code": "knp6",
            "cross_section_details": {
                "shape": 5,
                "width": "1.2 1.2 0",
                "height": "0 0.6 0.6",
                "code": "rectangle_w1.2_h0.6",
            },
            "discharge_coefficient_positive": None,
            "discharge_coefficient_negative": None,
            "sewerage": True,
            "max_capacity": 2.0,
            "crest_type": 4,
            "crest_level": -2.0,
            "cross_section_code": "rectangle_w1.2_h0.6",
        }
        self.threedi.import_hydx(self.hydx)
        assert self.threedi.orifices[3] == orifice_3
