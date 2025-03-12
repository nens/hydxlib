# -*- coding: utf-8 -*-
"""Tests for importer.py"""

import pytest
from geoalchemy2.shape import from_shape
from shapely import wkt
from threedi_schema import models

from hydxlib.exporter import (
    export_threedi,
    get_connection_node,
    get_cross_section_fields,
    get_line_between_nodes,
    get_node_geom,
    get_start_and_end_connection_node,
    write_threedi_to_db,
)
from hydxlib.threedi import Threedi


class TestGetCrossSectionFields:
    def test_get_cross_section_fields_not_tabulated(self):
        connection = {"code": "conn1", "cross_section_code": "cs1"}
        cross_section_dict = {"cs1": {"shape": 1, "width": "4.2", "height": "2.1"}}
        updated_connection = get_cross_section_fields(connection, cross_section_dict)
        assert updated_connection["cross_section_shape"] == 1
        assert updated_connection["cross_section_width"] == "4.2"
        assert updated_connection["cross_section_height"] == "2.1"

    def test_get_cross_section_fields_with_missing_definition(self, caplog):
        connection = {"code": "conn2", "cross_section_code": "missing_cs"}
        cross_section_dict = {"cs1": {"shape": 1, "width": "4.2", "height": "2.1"}}
        updated_connection = get_cross_section_fields(connection, cross_section_dict)
        assert updated_connection == connection
        assert caplog.records[0].levelname == "ERROR"

    def test_get_cross_section_fields_tabulated_YZ(self):
        connection = {"code": "conn3", "cross_section_code": "cs_tabulated"}
        cross_section_dict = {
            "cs_tabulated": {
                "shape": 7,
                "width": "1.1 2.2 3.3",
                "height": "0.1 0.2 0.3",
            }
        }
        updated_connection = get_cross_section_fields(connection, cross_section_dict)
        assert updated_connection["cross_section_shape"] == 7
        assert updated_connection["cross_section_table"] == "1.1,0.1\n2.2,0.2\n3.3,0.3"

    def test_get_cross_section_fields_tabulated_other(self):
        connection = {"code": "conn4", "cross_section_code": "cs_tabulated"}
        cross_section_dict = {
            "cs_tabulated": {
                "shape": 6,
                "width": "0.1 0.2 0.3",
                "height": "1.1 2.2 3.3",
            }
        }
        updated_connection = get_cross_section_fields(connection, cross_section_dict)
        assert updated_connection["cross_section_shape"] == 6
        assert updated_connection["cross_section_table"] == "1.1,0.1\n2.2,0.2\n3.3,0.3"


def test_get_node_geom():
    connection = {"code": "pmp1", "nodeA.code": "knp3", "nodeB.code": "knp4"}
    connection_node_dict = {"knp3": {"geom": "foo"}}
    assert get_node_geom(connection, connection_node_dict, "nodeA.code") == "foo"


def test_get_node_geom_missing(caplog):
    connection = {"code": "pmp1", "nodeA.code": "knp3", "nodeB.code": "knp4"}
    connection_node_dict = {"knp3": {"geom": "foo"}}
    assert get_node_geom(connection, connection_node_dict, "nodeB.code") is None
    assert caplog.records[0].levelname == "ERROR"


def test_get_line_between_nodes():
    geom1 = from_shape(wkt.loads("POINT (400 50)"), srid=28992)
    geom2 = from_shape(wkt.loads("POINT (400 60)"), srid=28992)
    connection = {"code": "pmp1", "nodeA.code": "knp3", "nodeB.code": "knp4"}
    connection_node_dict = {"knp3": {"geom": geom1}, "knp4": {"geom": geom2}}
    line = get_line_between_nodes(
        connection, connection_node_dict, "nodeA.code", "nodeB.code", target_epsg=28992
    )
    assert line["geom"] == "SRID=28992;LINESTRING (400.0 50.0, 400.0 60.0)"


def test_get_line_between_nodes_incomplete(caplog):
    connection = {"code": "pmp1", "nodeA.code": "knp3", "nodeB.code": "knp4"}
    connection_node_dict = {"knp3": {"geom": "foo"}}
    line = get_line_between_nodes(
        connection, connection_node_dict, "nodeA.code", "nodeB.code", target_epsg=28992
    )
    assert line["geom"] is None
    assert caplog.records[0].levelname == "ERROR"


def test_get_connection_node():
    connection = {"code": "pmp1", "foo": "knp3"}
    connection_node_dict = {"knp3": {"id": 3060}, "knp4": {"id": 3061}}
    assert get_connection_node(connection, connection_node_dict, "foo") == 3060


def test_get_connection_node_missing(caplog):
    connection = {"code": "pmp1", "foo": "knp300"}
    connection_node_dict = {"knp3": {"id": 3060}, "knp4": {"id": 3061}}
    assert get_connection_node(connection, connection_node_dict, "foo") is None
    assert caplog.records[0].levelname == "ERROR"


def test_get_start_and_end_connection_node():
    connection = {"code": "pmp1", "start_node.code": "knp3", "end_node.code": "knp4"}
    connection_node_dict = {"knp3": {"id": 3060}, "knp4": {"id": 3061}}
    connection = get_start_and_end_connection_node(connection, connection_node_dict)
    assert connection["connection_node_id_start"] == 3060
    assert connection["connection_node_id_end"] == 3061


@pytest.fixture
def hydx_setup(hydx):
    threedi = Threedi()
    threedi.import_hydx(hydx)
    return hydx, threedi


def test_export_threedi(hydx_setup, mock_exporter_db):
    output = export_threedi(hydx_setup[0], "/some/path")
    assert len(output.connection_nodes) == 85


def test_write_to_db(hydx_setup, mock_exporter_db, threedi_db):
    commit_counts_expected = {
        "connection_nodes": 85,
        "pipes": 80,
        "pumps": 8,
        "weirs": 6,
        "orifices": 2,
        "outlets": 3,
        "surfaces": 262,
        "dry_weather_flows": 67,
    }
    commit_counts = write_threedi_to_db(hydx_setup[1], {"db_file": "/some/path"})
    assert commit_counts == commit_counts_expected

    session = threedi_db.get_session()

    assert (
        session.query(models.ConnectionNode)
        .filter(models.ConnectionNode.geom.isnot(None))
        .count()
        == commit_counts_expected["connection_nodes"]
    )
    MODELS = {
        "pumps": models.Pump,
        "weirs": models.Weir,
        "orifices": models.Orifice,
        "surfaces": models.Surface,
        "dry_weather_flows": models.DryWeatherFlow,
        "pipes": models.Pipe,
        "outlets": models.BoundaryCondition1D,
    }
    for name, model in MODELS.items():
        assert session.query(model).count() == commit_counts_expected[name]
