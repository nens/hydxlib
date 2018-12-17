# -*- coding: utf-8 -*-
"""Tests for threedi.py"""
from gwswlib.threedi import Threedi


def test_get_manhole_shape(caplog):
    shape_code = 'RND'
    record_code = 'test'
    Threedi.get_manhole_shape(shape_code, record_code)
    assert "Unknown" not in caplog.text
