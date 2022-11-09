# -*- coding: utf-8 -*-
"""Tests for threedi.py"""
from hydxlib.threedi import check_if_element_is_created_with_same_code
from hydxlib.threedi import get_hydx_default_profile
from hydxlib.threedi import Threedi
from unittest import mock


MANHOLE_SHAPE_RECTANGLE = "rect"
MANHOLE_SHAPE_ROUND = "rnd"


def test_get_mapping_value_wrong(caplog):
    MANHOLE_SHAPE_MAPPING = {
        "RND": MANHOLE_SHAPE_ROUND,
        "RHK": MANHOLE_SHAPE_RECTANGLE,
    }
    shape_code = "SQR"
    record_code = "01_TEST"
    threedi = Threedi()
    threedi.get_mapping_value(
        MANHOLE_SHAPE_MAPPING, shape_code, record_code, name_for_logging="manhole shape"
    )
    assert "01_TEST has an unknown manhole shape: SQR" in caplog.text


def test_get_mapping_value_right():
    MANHOLE_SHAPE_MAPPING = {
        "RND": MANHOLE_SHAPE_ROUND,
        "RHK": MANHOLE_SHAPE_RECTANGLE,
    }
    shape_code = "RND"
    record_code = "01_TEST"
    threedi = Threedi()
    shape = threedi.get_mapping_value(
        MANHOLE_SHAPE_MAPPING, shape_code, record_code, name_for_logging="manhole shape"
    )
    assert shape == "rnd"


def test_get_mapping_value_missing(caplog):
    threedi = Threedi()
    actual = threedi.get_mapping_value(
        {}, None, "01_TEST", name_for_logging="manhole shape"
    )
    assert not caplog.text
    assert actual is None


def test_check_if_element_created_is_with_same_code(caplog):
    checked_element = "knp6"
    created_elements = [
        {"code": "knp1", "initial_waterlevel": None, "geom": (400, 50, 28992)},
        {"code": "knp6", "initial_waterlevel": None, "geom": (400, 350, 28992)},
    ]
    element_type = "Connection node"
    check_if_element_is_created_with_same_code(
        checked_element, created_elements, element_type
    )
    assert "Multiple elements 'Connection node' are created" in caplog.text


def test_import_hydx_unknown_connection_types(caplog):
    hydx = mock.Mock()
    hydx.connection_nodes = []
    hydx.structures = []
    hydx.surfaces = []
    hydx.discharges = []
    hydx.connections = [
        mock.Mock(identificatieknooppuntofverbinding="ovs82", typeverbinding="XXX")
    ]
    threedi = Threedi()
    threedi.import_hydx(hydx)
    assert '"typeverbinding" is not recognized' in caplog.text


def test_structure_does_not_exist_error(caplog):
    hydx = mock.Mock()
    hydx.structures = []
    hydx.connection_nodes = []
    hydx.surfaces = []
    hydx.discharges = []
    hydx.connections = [
        mock.Mock(identificatieknooppuntofverbinding="pmp1", typeverbinding="PMP")
    ]
    threedi = Threedi()
    threedi.import_hydx(hydx)
    assert "Structure does not exist for connection" in caplog.text


def test_get_hydx_default_profile():
    profile = get_hydx_default_profile()
    assert profile.breedte_diameterprofiel == "1000"


def test_import_hydx(hydx):
    threedi = Threedi()
    threedi.import_hydx(hydx)
    assert len(threedi.connection_nodes) == 85
    assert threedi.connection_nodes[0] == {
        "code": "knp1",
        "initial_waterlevel": None,
        "geom": (400, 50, 28992),
        "storage_area": 50.0,
    }
    assert threedi.manholes[0] == {
        "code": "knp1",
        "display_name": "1001",
        "surface_level": 2.75,
        "width": 7.071,
        "length": 7.071,
        "shape": "rnd",
        "bottom_level": 0,
        "calculation_type": 2,
        "manhole_indicator": 0,
    }
    assert threedi.pumpstations[0] == {
        "code": "pmp88",
        # check if connection number 1 is created for second structure with these nodes
        "display_name": "2001-1016-1",
        "start_node.code": "knp72",
        "end_node.code": "knp15",
        "type_": 1,
        "start_level": 0.5,
        "lower_stop_level": 0,
        "upper_stop_level": None,
        "capacity": 20,
        "sewerage": True,
    }
    assert threedi.pipes[0] == {
        "code": "lei1",
        # check if connection number 1 is created for second structure with these nodes
        "display_name": "1003-1004-1",
        "start_node.code": "knp3",
        "end_node.code": "knp4",
        "sewerage_type": 0,
        "invert_level_start_point": 0.10,
        "invert_level_end_point": 0.00,
        "original_length": 48.0,
        "material": 0,
        "sewerage_type": 0,
        "calculation_type": 1,
        "cross_section_details": {
            "code": "round_1.1",
            "shape": 2,
            "width": 1.1,
            "height": None,
        },
        "cross_section_code": "round_1.1",
    }
    assert threedi.impervious_surfaces[0] == {
        "code": "1",
        "display_name": "knp8",
        "area": 9.0,
        "surface_class": "gesloten verharding",
        "surface_inclination": "uitgestrekt",
    }
    assert threedi.impervious_surfaces[262] == {
        "code": "263",
        "display_name": "knp61",
        "area": 0.0,
        "surface_class": "gesloten verharding",
        "surface_inclination": "vlak",
        "dry_weather_flow": 60.0,
        "nr_of_inhabitants": "2",
    }
    assert threedi.outlets[0] == {
        "node.code": "knp78",
        "timeseries": "0,-5.0\n9999,-5.0",
        "boundary_type": 1,
    }
    # select first manhole from dataset for check
    connection = hydx.connections[90]
    structure = hydx.structures[13]
    threedi.add_structure(connection, structure)
    assert threedi.pumpstations[8]["type_"] == 2
    assert threedi.weirs[1] == {
        "code": "ovs83",
        "display_name": "1009-1009-1",
        "start_node.code": "knp8",
        "end_node.code": "knp55",
        "cross_section_details": {
            "code": "rectangle_w3.0_open",
            "shape": 1,
            "width": 3.0,
            "height": None,
        },
        "crest_type": 4,
        "crest_level": 2.7,
        "discharge_coefficient_positive": 0.9,
        "discharge_coefficient_negative": 0.9,
        "sewerage": True,
        "cross_section_code": "rectangle_w3.0_open",
    }
    assert threedi.orifices[1] == {
        "code": "drl97",
        "display_name": "2002-2002-1",
        "start_node.code": "knp16",
        "end_node.code": "knp60",
        "cross_section_details": {"shape": 2, "width": 0.4, "height": None},
        "discharge_coefficient_positive": 0,
        "discharge_coefficient_negative": 0.8,
        "sewerage": True,
        "crest_type": 4,
        "crest_level": 0.0,
        "cross_section_code": "round_0.4",
    }
