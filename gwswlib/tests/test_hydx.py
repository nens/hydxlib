# -*- coding: utf-8 -*-
"""Tests for hydx.py"""
from collections import OrderedDict

from gwswlib.hydx import ConnectionNode


def test_check_init_connectionnode():
    line = OrderedDict(
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
    connection_node = ConnectionNode(codes=line)
    print(connection_node.node)
    x
