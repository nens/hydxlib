# -*- coding: utf-8 -*-
"""Tests for importer.py"""
from unittest import TestCase
import pytest

from gwswlib.sql_models.threedi_database import ThreediDatabase
from gwswlib.importer import import_hydx
from gwswlib.threedi import Threedi
from gwswlib.exporter import export_threedi, write_threedi_to_db


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
        }
        commit_counts = write_threedi_to_db(self.threedi, self.threedi_db_settings)
        assert commit_counts == commit_counts_expected
