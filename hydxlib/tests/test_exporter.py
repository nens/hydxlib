# -*- coding: utf-8 -*-
"""Tests for importer.py"""
from hydxlib.exporter import export_json
from hydxlib.exporter import export_threedi
from hydxlib.exporter import get_cross_section_definition_id
from hydxlib.exporter import get_start_and_end_connection_node
from hydxlib.exporter import write_threedi_to_db
from hydxlib.threedi import Threedi
from threedi_modelchecker.threedi_model import models

import json
import pytest


def test_get_start_and_end_connection_node_right():
    connection = {"code": "pmp1", "start_node.code": "knp3", "end_node.code": "knp4"}
    connection_node_dict = {"knp3": 3060}
    connection = get_start_and_end_connection_node(connection, connection_node_dict)
    assert connection["connection_node_start_id"] == 3060


def test_get_start_and_end_connection_node_wrong(caplog):
    connection = {"code": "pmp1", "start_node.code": "knp31", "end_node.code": "knp41"}
    connection_node_dict = {"knp3": 3060, "knp4": 3061}
    connection = get_start_and_end_connection_node(connection, connection_node_dict)
    assert "End node of connection" in caplog.text


def test_get_cross_section_definition_id_wrong(caplog):
    connection = {"code": "drl5", "cross_section_code": "round_1000"}
    cross_section_dict = {"round_1001": 362}
    connection = get_cross_section_definition_id(connection, cross_section_dict)
    assert "Cross section" in caplog.text


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
        "manholes": 84,
        "pumpstations": 8,
        "weirs": 6,
        "cross_sections": 54,
        "orifices": 2,
        "impervious_surfaces": 330,
        "pipes": 80,
        "outlets": 3,
    }
    commit_counts = write_threedi_to_db(hydx_setup[1], {"db_file": "/some/path"})
    assert commit_counts == commit_counts_expected

    session = threedi_db.get_session()

    assert (
        session.query(models.ConnectionNode)
        .filter(models.ConnectionNode.the_geom != None)
        .count()
        == commit_counts_expected["connection_nodes"]
    )
    MODELS = {
        "manholes": models.Manhole,
        "pumpstations": models.Pumpstation,
        "weirs": models.Weir,
        "cross_sections": models.CrossSectionDefinition,
        "orifices": models.Orifice,
        "impervious_surfaces": models.ImperviousSurface,
        "pipes": models.Pipe,
        "outlets": models.BoundaryCondition1D,
    }
    for name, model in MODELS.items():
        assert session.query(model).count() == commit_counts_expected[name]


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
