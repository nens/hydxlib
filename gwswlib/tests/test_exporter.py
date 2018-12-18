# -*- coding: utf-8 -*-
"""Tests for importer.py"""
from gwswlib.sql_models.threedi_database import ThreediDatabase
from gwswlib.importer import import_hydx
from gwswlib.threedi import Threedi
from gwswlib.exporter import write_threedi_to_db


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


def test_write_to_db_con_nodes_huge():
    # cause idon't know how to mock or make an object
    hydx_path = "gwswlib/tests/example_files_structures_hydx/"
    hydx = import_hydx(hydx_path)
    threedi = Threedi()
    threedi.import_hydx(hydx)
    # real test
    commit_counts = write_threedi_to_db(threedi)
    assert "connection_nodes" in commit_counts
