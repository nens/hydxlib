# -*- coding: utf-8 -*-
"""Tests for threedi.py"""
from gwswlib.threedi import Threedi

from mock import patch


@patch("gwswlib.threedi.Threedi")
def test_get_manhole_shape(caplog):
    shape_code = "RXND"
    record_code = "01_TEST"
    threedi = Threedi()
    threedi.get_manhole_shape(shape_code, record_code)
    print(caplog.text)
    assert "Unknown" in caplog.text
