# -*- coding: utf-8 -*-
"""Tests for hydx.py"""
from collections import OrderedDict
from hydxlib.hydx import check_headers
from hydxlib.hydx import Connection
from hydxlib.hydx import ConnectionNode
from hydxlib.hydx import Discharge
from hydxlib.hydx import Profile
from hydxlib.hydx import Structure
from hydxlib.hydx import Surface
from hydxlib.hydx import Variation

import logging
import pytest


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


def test_touch_csvheaders_hydxelement():
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
            ("WOS_OPP", "1.a"),  # invalid
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
        "identificatieknooppuntofverbinding": "knp1",
        "identificatierioolstelsel": "GEMENGD-13 Nijrees",
        "identificatierioolput": "13_990100",
        "x_coordinaat": 241330.836,
        "y_coordinaat": 483540.234,
        "identificatiecompartiment": None,
        "niveaumaaiveld": None,
        "maaiveldschematisering": None,
        "oppervlakwateropstraat": None,
        "materiaalput": None,
        "vormput": None,
        "niveaubinnenonderkantput": None,
        "breedte_diameterputbodem": None,
        "lengteputbodem": None,
        "typeknooppunt": "INS",
        "initielewaterstand": None,
        "statusobject": None,
        "aannamemaaiveldhoogte": None,
        "identificatiedefinitieit_object": None,
        "toelichtingregel": None,
    }
    connection_node = ConnectionNode.import_csvline(csvline=line_in)
    assert connection_node.dict() == line_out


def test_check_init_connection():
    line_in = OrderedDict(
        [
            ("UNI_IDE", "ovs1"),
            ("KN1_IDE", "knp1"),
            ("KN2_IDE", "knp2"),
            ("VRB_TYP", "OVS"),
            ("LEI_IDE", ""),
            ("BOB_KN1", ""),
            ("BOB_KN2", ""),
            ("STR_RCH", "OPN"),
            ("VRB_LEN", ""),
            ("INZ_TYP", ""),
            ("ITO_IDE", ""),
            ("PRO_IDE", ""),
            ("STA_OBJ", ""),
            ("AAN_BB1", ""),
            ("AAN_BB2", ""),
            ("AAN_PRO", ""),
            ("INI_NIV", ""),
            ("ALG_TOE", ""),
        ]
    )
    line_out = {
        "identificatieknooppuntofverbinding": "ovs1",
        "identificatieknooppunt1": "knp1",
        "identificatieknooppunt2": "knp2",
        "typeverbinding": "OVS",
        "identificatieleiding": None,
        "bobknooppunt1": None,
        "bobknooppunt2": None,
        "stromingsrichting": "OPN",
        "lengteverbinding": None,
        "typeinzameling": None,
        "identificatiedefinitieit_object": None,
        "identificatieprofieldefinitie": None,
        "statusobject": None,
        "aannamebobknooppunt1": None,
        "aannamebobknooppunt2": None,
        "aannameprofiel": None,
        "initielewaterstand": None,
        "toelichtingregel": None,
    }
    connection = Connection.import_csvline(csvline=line_in)
    assert connection.dict() == line_out


def test_check_on_unique(hydx, caplog):
    caplog.set_level(logging.ERROR)
    hydx._check_on_unique(hydx.connection_nodes, "identificatieknooppuntofverbinding")
    assert len(caplog.records) == 1
    assert (
        caplog.records[0].message
        == "Non-unique 'identificatieknooppuntofverbinding' value encountered in Knooppunt knp9"
    )


def test_check_init_structure():
    line_in = OrderedDict(
        [
            ("UNI_IDE", "ovs1"),
            ("KWK_TYP", "OVS"),
            ("BWS_NIV", ""),
            ("PRO_BOK", ""),
            ("DRL_COE", ""),
            ("DRL_CAP", ""),
            ("OVS_BRE", "1.5"),
            ("OVS_NIV", "9.5"),
            ("OVS_VOH", ""),
            ("OVS_COE", "0.8"),
            ("PMP_CAP", ""),
            ("PMP_AN1", ""),
            ("PMP_AF1", ""),
            ("PMP_AN2", ""),
            ("PMP_AF2", ""),
            ("QDH_NIV", ""),
            ("QDH_DEB", ""),
            ("AAN_OVN", ""),
            ("AAN_OVB", ""),
            ("AAN_CAP", ""),
            ("AAN_ANS", ""),
            ("AAN_AFS", ""),
            ("ALG_TOE", ""),
        ]
    )
    line_out = {
        "identificatieknooppuntofverbinding": "ovs1",
        "typekunstwerk": "OVS",
        "buitenwaterstand": None,
        "niveaubinnenonderkantprofiel": None,
        "contractiecoefficientdoorlaatprofiel": None,
        "maximalecapaciteitdoorlaat": None,
        "breedteoverstortdrempel": 1.5,
        "niveauoverstortdrempel": 9.5,
        "vrijeoverstorthoogte": None,
        "afvoercoefficientoverstortdrempel": 0.8,
        "pompcapaciteit": None,
        "aanslagniveaubenedenstrooms": None,
        "afslagniveaubenedenstrooms": None,
        "aanslagniveaubovenstrooms": None,
        "afslagniveaubovenstrooms": None,
        "niveauverschildebiet_verhangrelatie": None,
        "debietverschildebiet_verhangrelatie": None,
        "aannameniveauoverstortdrempel": None,
        "aannamebreedteoverstortdrempel": None,
        "aannamepompcapaciteitpomp": None,
        "aannameaanslagniveaupomp": None,
        "aannameafslagniveaupomp": None,
        "toelichtingregel": None,
    }
    structure = Structure.import_csvline(csvline=line_in)
    assert structure.dict() == line_out


def test_check_init_profile():
    line_in = OrderedDict(
        [
            ("PRO_IDE", "PVC160"),
            ("PRO_MAT", "PVC"),
            ("PRO_VRM", "RND"),
            ("PRO_BRE", "160"),
            ("PRO_HGT", ""),
            ("TAB_BRE", ""),
            ("TAB_HGT", ""),
            ("ALG_TOE", "Standaard maat"),
        ]
    )
    line_out = {
        "identificatieprofieldefinitie": "PVC160",
        "materiaal": "PVC",
        "vormprofiel": "RND",
        "breedte_diameterprofiel": "160",
        "hoogteprofiel": None,
        "tabulatedbreedte": None,
        "tabulatedhoogte": None,
        "toelichtingregel": "Standaard maat",
    }
    profile = Profile.import_csvline(csvline=line_in)
    assert profile.dict() == line_out


def test_check_init_surface():
    line_in = OrderedDict(
        [
            ("UNI_IDE", "knp8"),
            ("NSL_STA", "DeBilt"),
            ("AFV_DEF", "nwrw.csv"),
            ("AFV_IDE", "GVH_VLU"),
            ("AFV_OPP", "9"),
            ("ALG_TOE", ""),
        ]
    )
    line_out = {
        "identificatieknooppuntofverbinding": "knp8",
        "neerslagstation": "DeBilt",
        "afvoerconcept": "nwrw.csv",
        "afvoerkenmerken": "GVH_VLU",
        "afvoerendoppervlak": 9.0,
        "toelichtingregel": None,
    }
    connection_node = Surface.import_csvline(csvline=line_in)
    assert connection_node.dict() == line_out


@pytest.mark.parametrize(
    "cls",
    [Connection, ConnectionNode, Profile, Structure, Surface, Discharge, Variation],
)
def test_repr_uninitialized(cls):
    assert repr(cls())


@pytest.mark.parametrize(
    "cls",
    [Connection, ConnectionNode, Profile, Structure, Surface, Discharge, Variation],
)
def test_str_uninitialized(cls):
    assert str(cls())
