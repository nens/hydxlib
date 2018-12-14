# -*- coding: utf-8 -*-
"""Tests for scripts.py"""
from gwswlib import scripts

import mock


@mock.patch("sys.argv", ["program"])
def test_get_parser():
    parser = scripts.get_parser()
    # As a test, we just check one option. That's enough.
    options = parser.parse_args()
    assert options.verbose is False
