from unittest import mock

import pytest
from threedi_schema import ThreediDatabase

from hydxlib.importer import import_hydx


@pytest.fixture
def threedi_db():
    db = ThreediDatabase("")
    schema = db.schema
    schema.upgrade(backup=False)
    return db


@pytest.fixture
def mock_exporter_db(threedi_db):
    with mock.patch("hydxlib.exporter.ThreediDatabase") as m:
        m.return_value = threedi_db
        yield m


@pytest.fixture(scope="session")
def hydx():
    hydx_path = "hydxlib/tests/example_files_structures_hydx/"
    return import_hydx(hydx_path)
