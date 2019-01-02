# -*- coding: utf-8 -*-
"""Tests for importer.py"""
from unittest import TestCase
import pytest
from collections import OrderedDict

from gwswlib.sql_models.threedi_database import ThreediDatabase
from gwswlib.importer import import_hydx
from gwswlib.threedi import Threedi
from gwswlib.exporter import export_threedi, write_threedi_to_db
from gwswlib.hydx import Hydx, Connection


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


def test_import_hydx_unknown_connection_types(caplog):
    # TODO ik zou graag in één keer die hydx.connections willen maken zonder .import_csvline te gebruiken. Is dat mogelijk?
    # daarbij zou ik de line_out uit test_check_init_connection in test.hydx.py willen gebruiken.
    unknown_connection_line = OrderedDict(
        [
            ("UNI_IDE", "ovs1"),
            ("KN1_IDE", "knp1"),
            ("KN2_IDE", "knp2"),
            ("VRB_TYP", "XXX"),
            ("LEI_IDE", ""),
            ("BOB_KN1", ""),
            ("BOB_KN2", ""),
            ("STR_RCH", "OPN"),
            ("VRB_LEN", ""),
            ("INZ_TYP", ""),
            ("INV_KN1", ""),
            ("UTV_KN1", ""),
            ("INV_KN2", ""),
            ("UTV_KN2", ""),
            ("ITO_IDE", ""),
            ("PRO_IDE", ""),
            ("STA_OBJ", ""),
            ("AAN_BB1", ""),
            ("AAN_BB2", ""),
            ("INI_NIV", ""),
            ("ALG_TOE", ""),
        ]
    )
    hydx = Hydx()
    connection = Connection()
    connection.import_csvline(unknown_connection_line)
    hydx.connections.append(connection)
    threedi = Threedi()
    threedi.import_hydx(hydx)
    assert '"typeverbinding" is not recognized' in caplog.text


def test_import_hydx_known_pipe_connection(caplog):
    # TODO ik zou graag in één keer die hydx.connections willen maken zonder .import_csvline te gebruiken. Is dat mogelijk?
    # daarbij zou ik de line_out uit test_check_init_connection in test.hydx.py willen gebruiken.
    connection_line_pipe = OrderedDict(
        [
            ("UNI_IDE", "ovs1"),
            ("KN1_IDE", "knp1"),
            ("KN2_IDE", "knp2"),
            ("VRB_TYP", "GSL"),
            ("LEI_IDE", ""),
            ("BOB_KN1", ""),
            ("BOB_KN2", ""),
            ("STR_RCH", "OPN"),
            ("VRB_LEN", ""),
            ("INZ_TYP", ""),
            ("INV_KN1", ""),
            ("UTV_KN1", ""),
            ("INV_KN2", ""),
            ("UTV_KN2", ""),
            ("ITO_IDE", ""),
            ("PRO_IDE", ""),
            ("STA_OBJ", ""),
            ("AAN_BB1", ""),
            ("AAN_BB2", ""),
            ("INI_NIV", ""),
            ("ALG_TOE", ""),
        ]
    )
    hydx = Hydx()
    connection = Connection()
    connection.import_csvline(connection_line_pipe)
    hydx.connections.append(connection)
    threedi = Threedi()
    threedi.import_hydx(hydx)
    assert '"typeverbinding" is not connected' in caplog.text


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
        commit_counts_expected = {"connection_nodes": 7, "manholes": 6}
        commit_counts = write_threedi_to_db(self.threedi, self.threedi_db_settings)
        assert commit_counts == commit_counts_expected
