# -*- coding: utf-8 -*-
"""Tests for scripts.py"""
from gwswlib.importer import check_headers


def test_check_headers(caplog):
    a = [1, 2, 3]
    b = [2, 3, 4]
    check_headers(a, b)
    assert "missing columns" in caplog.text
    assert "extra columns" in caplog.text


def test_check_headers_2(caplog):
    a = [1, 2, 3]
    b = [1, 2, 3]
    check_headers(a, b)
    assert "missing columns" not in caplog.text
    assert "extra columns" not in caplog.text
