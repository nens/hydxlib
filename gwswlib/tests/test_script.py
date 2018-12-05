# -*- coding: utf-8 -*-
"""Tests for script.py"""
from gwswlib import script


def test_get_parser():
    parser = script.get_parser()
    # As a test, we just check one option. That's enough.
    options = parser.parse_args()
    assert options.verbose is False
