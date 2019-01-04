# -*- coding: utf-8 -*-
"""Tests for importer.py"""
from unittest import TestCase
import pytest

from gwswlib.sql_models.threedi_database import ThreediDatabase
from gwswlib.importer import import_hydx
from gwswlib.threedi import Threedi
from gwswlib.exporter import (
    export_threedi,
    write_threedi_to_db,
    get_cross_section_definition_id,
    get_start_and_end_connection_node,
)


def test_check_connection_db(caplog):
    # temporarily db setup!
    db = ThreediDatabase(
        {
            "host": "localhost",
            "port": "5432",
            "database": "test_gwsw",
            "username": "postgres",
            "password": "postgres",
        },
        "postgres",
    )

    session = db.get_session()
    assert session is not None


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


class TestThreedi(TestCase):
    def setUp(self):
        self.threedi = Threedi()
        hydx_path = "gwswlib/tests/example_files_structures_hydx/"
        self.threedi_db_settings = {
            "threedi_dbname": "test_gwsw",
            "threedi_host": "localhost",
            "threedi_user": "postgres",
            "threedi_password": "postgres",
            "threedi_port": 5432,
        }
        self.hydx = import_hydx(hydx_path)
        self.threedi.import_hydx(self.hydx)

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    def test_export_threedi(self):
        output = export_threedi(self.hydx, self.threedi_db_settings)
        assert len(output.connection_nodes) == 7

    def test_write_to_db_con_nodes_huge(self):
        commit_counts_expected = {
            "connection_nodes": 7,
            "manholes": 6,
            "pumpstations": 5,
            "weirs": 3,
            "cross_sections": 7,
            "orifices": 5,
        }
        commit_counts = write_threedi_to_db(self.threedi, self.threedi_db_settings)
        assert commit_counts == commit_counts_expected
