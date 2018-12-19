# -*- coding: utf-8 -*-
"""Tests for threedi.py"""
from gwswlib.threedi import Threedi


def test_get_manhole_shape_wrong(caplog):
    shape_code = "SQR"
    record_code = "01_TEST"
    threedi = Threedi()
    threedi.get_manhole_shape(shape_code, record_code)
    assert "Unknown" in caplog.text


def test_check_manhole_shape_right(caplog):
    shape_code = "RND"
    record_code = "01_TEST"
    threedi = Threedi()
    shape = threedi.get_manhole_shape(shape_code, record_code)
    assert shape == "rnd"
