# -*- coding: utf-8 -*-
"""Tests for hydx.py"""
from collections import OrderedDict

from gwswlib.hydx import ConnectionNode


def test_touch_csvheaders():
    csvheaders = ConnectionNode.csvheaders()
    assert "INI_NIV" in csvheaders


def test_check_init_connectionnode():
    line_in = OrderedDict(
        [
            ("UNI_IDE", "knp1"),
            ("RST_IDE", "GEMENGD-13 Nijrees"),
            ("PUT_IDE", "13_990100"),
            ("KNP_XCO", "241330.836"),
            ("KNP_YCO", "483540.234"),
            ("CMP_IDE", ""),
            ("MVD_NIV", ""),
            ("MVD_SCH", ""),
            ("WOS_OPP", ""),
            ("KNP_MAT", ""),
            ("KNP_VRM", ""),
            ("KNP_BOK", ""),
            ("KNP_BRE", ""),
            ("KNP_LEN", ""),
            ("KNP_TYP", "INS"),
            ("INI_NIV", ""),
            ("STA_OBJ", ""),
            ("AAN_MVD", ""),
            ("ITO_IDE", ""),
            ("ALG_TOE", ""),
        ]
    )
    line_out = {
        "UNI_IDE": "knp1",
        "RST_IDE": "GEMENGD-13 Nijrees",
        "PUT_IDE": "13_990100",
        "KNP_XCO": 241330.836,
        "KNP_YCO": 483540.234,
        "CMP_IDE": None,
        "MVD_NIV": None,
        "MVD_SCH": None,
        "WOS_OPP": None,
        "KNP_MAT": None,
        "KNP_VRM": None,
        "KNP_BOK": None,
        "KNP_BRE": None,
        "KNP_LEN": None,
        "KNP_TYP": "INS",
        "INI_NIV": None,
        "STA_OBJ": None,
        "AAN_MVD": None,
        "ITO_IDE": None,
        "ALG_TOE": None,
    }
    connection_node = ConnectionNode(data=line_in).run_import()
    assert connection_node == line_out
