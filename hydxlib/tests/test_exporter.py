# -*- coding: utf-8 -*-
"""Tests for importer.py"""
import json

import pytest
from threedi_schema import models

from hydxlib.exporter import (
    export_json,
    export_threedi,
    get_cross_section_fields,
    get_start_and_end_connection_node,
    write_threedi_to_db,
)
from hydxlib.threedi import Threedi


def test_get_start_and_end_connection_node_right():
    connection = {"code": "pmp1", "start_node.code": "knp3", "end_node.code": "knp4"}
    connection_node_dict = {"knp3": {"id": 3060, "geom": None}}
    connection = get_start_and_end_connection_node(connection, connection_node_dict)
    assert connection["connection_node_id_start"] == 3060


def test_get_start_and_end_connection_node_wrong(caplog):
    connection = {"code": "pmp1", "start_node.code": "knp31", "end_node.code": "knp41"}
    connection_node_dict = {"knp3": {"id": 3060}, "knp4": {"id": 3061}}
    connection = get_start_and_end_connection_node(connection, connection_node_dict)
    assert all([log.levelname == "ERROR" for log in caplog.records])
    assert connection["connection_node_id_start"] is None
    assert connection["connection_node_id_end"] is None


#TODO: add unit tests


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


@pytest.mark.skip()
def test_export_json(hydx_setup, tmp_path):
    json_path = tmp_path / "export.json"
    export_json(hydx_setup[0], json_path)

    with open(json_path, "r") as f:
        data = json.load(f)

    obj_count_expected = {
        "connection_nodes": 85,
        "manholes": 85,
        "pumpstations": 8,
        "weirs": 6,
        "cross_sections": 54,
        "orifices": 2,
        "impervious_surfaces": 330,
        "impervious_surface_maps": 330,
        "pipes": 80,
        "outlets": 3,
        "connections": 0,
    }
    obj_count_actual = {k: len(data[k]) for k in data}

    assert obj_count_expected == obj_count_actual
