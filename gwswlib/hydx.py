# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)


class Hydx:
    def __init__(self):
        self.connection_nodes = []


class ConnectionNode:
    MAAIVELDSCHEMATISERINGCOLL = [
        {"RES": "Reservoir"},
        {"KNV": "Gekneveld"},
        {"VRL": "Verlies"},
    ]

    MATERIAALHYDXCOLL = [
        {"BET": "Beton"},
        {"BET": "Gewapend beton"},
        {"PVC": "Polyvinylchloride"},
        {"GRE": "Gres"},
        {"GIJ": "Gietijzer"},
        {"MSW": "Metselwerk"},
        {"MSW": "Metselwerk (baksteen)"},
        {"MSW": "Metselwerk (bepleisterd)"},
        {"MSW": "Metselwerk (onbepleisterd)"},
        {"HPE": "HDPE"},
        {"HPE": "Polyester"},
        {"HPE": "Polyetheen"},
        {"HPE": "Polypropyleen"},
        {"PIJ": "Plaatijzer"},
        {"STL": "Staal"},
    ]

    VORMPUTCOLL = [{"RHK": "Rechthoekig"}, {"RND": "Rond"}]

    TYPEKNOOPPUNTCOLL = [
        {"INS": "Inspectieput"},
        {"ITP": "Infiltratieput"},
        {"CMP": "Compartiment"},
        {"UIT": "Uitlaat"},
    ]

    STATUSOBJECTCOLL = [{"ACT": "In gebruik"}, {"ONT": "In ontwerp"}]

    AANNAMEHYDXCOLL = [
        {"EXJ": "Expert judgement"},
        {"ONT": "Conform ontwerp"},
        {"NRM": "Conform norm"},
    ]

    FIELDS = [
        {
            "csvheader": "UNI_IDE",
            "fieldname": "IdentificatieKnooppuntOfVerbinding",
            "type": str,
            "required": True,
        },
        {
            "csvheader": "RST_IDE",
            "fieldname": "IdentificatieRioolstelsel",
            "type": str,
            "required": False,
        },
        {
            "csvheader": "PUT_IDE",
            "fieldname": "IdentificatieRioolput",
            "type": str,
            "required": True,
        },
        {
            "csvheader": "KNP_XCO",
            "fieldname": "X_coordinaat",
            "type": float,
            "required": True,
        },
        {
            "csvheader": "KNP_YCO",
            "fieldname": "Y_coordinaat",
            "type": float,
            "required": True,
        },
        {
            "csvheader": "CMP_IDE",
            "fieldname": "IdentificatieCompartiment",
            "type": str,
            "required": False,
        },
        {
            "csvheader": "MVD_NIV",
            "fieldname": "NiveauMaaiveld",
            "type": float,
            "required": True,
        },
        {
            "csvheader": "MVD_SCH",
            "fieldname": "Maaiveldschematisering",
            "type": str,
            "required": True,
        },
        {
            "csvheader": "WOS_OPP",
            "fieldname": "OppervlakWaterOpStraat",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "KNP_MAT",
            "fieldname": "MateriaalPut",
            "type": str,
            "required": True,
        },
        {"csvheader": "KNP_VRM", "fieldname": "VormPut", "type": str, "required": True},
        {
            "csvheader": "KNP_BOK",
            "fieldname": "NiveauBinnenonderkantPut",
            "type": float,
            "required": True,
        },
        {
            "csvheader": "KNP_BRE",
            "fieldname": "Breedte_diameterPutbodem",
            "type": float,
            "required": True,
        },
        {
            "csvheader": "KNP_LEN",
            "fieldname": "LengtePutbodem",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "KNP_TYP",
            "fieldname": "TypeKnooppunt",
            "type": str,
            "required": True,
        },
        {
            "csvheader": "INI_NIV",
            "fieldname": "InitieleWaterstand",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "STA_OBJ",
            "fieldname": "StatusObject",
            "type": str,
            "required": False,
        },
        {
            "csvheader": "AAN_MVD",
            "fieldname": "AannameMaaiveldhoogte",
            "type": str,
            "required": False,
        },
        {
            "csvheader": "ITO_IDE",
            "fieldname": "IdentificatieDefinitieIT_object",
            "type": str,
            "required": False,
        },
        {
            "csvheader": "ALG_TOE",
            "fieldname": "ToelichtingRegel",
            "type": str,
            "required": False,
        },
    ]

    @classmethod
    def csvheaders(cls):
        return [field["csvheader"] for field in cls.FIELDS]

    def __init__(self):
        pass

    def __repr__(self):
        return "<ConnectionNode %s>" % getattr(self, "identificatierioolput", None)

    def import_csvline(self, csvline):
        for field in self.FIELDS:
            fieldname = field["fieldname"].lower()
            value = csvline[field["csvheader"]]
            datatype = field["type"]

            if value == "":
                value = None

            # set fields to defined data type and load into object
            if value is not None:
                setattr(self, fieldname, datatype(value))
            else:
                setattr(self, fieldname, None)

    def check(self):
        pass


class Connection:
    pass


class Structure:
    pass


class Meta:
    pass
