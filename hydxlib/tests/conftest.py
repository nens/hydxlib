from threedi_modelchecker import ThreediDatabase
from threedi_modelchecker.schema import ModelSchema
from unittest import mock

import pytest


@pytest.fixture
def threedi_db():
    db = ThreediDatabase("")
    schema = ModelSchema(db)
    schema.upgrade(backup=False)
    return db


@pytest.fixture
def mock_exporter_db(threedi_db):
    with mock.patch("hydxlib.exporter.ThreediDatabase") as m:
        m.return_value = threedi_db
        yield m
