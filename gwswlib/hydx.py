# -*- coding: utf-8 -*-
import logging
from collections import Counter

logger = logging.getLogger(__name__)


class Hydx:
    def __init__(self):
        self.connection_nodes = []

    def check_import_data(self):
        self._check_on_unique(
            self.connection_nodes, "identificatieknooppuntofverbinding"
        )

    def _check_on_unique(self, records, unique_field):
        values = [m.__dict__[unique_field] for m in records]
        counter = Counter(values)
        doubles = [key for key, count in counter.items() if count > 1]

        for double in doubles:
            logging.error(
                "double values in %s for records with %s %r",
                records[0].__class__.__name__,
                unique_field,
                double,
            )


class ConnectionNode:
    MAAIVELDSCHEMATISERINGCOLL = [
        {"RES": "Reservoir"},
        {"KNV": "Gekneveld"},
        {"VRL": "Verlies"},
    ]

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
        # AV - function looks like hydroObjectListFromSUFHYD in turtleurbanclasses.py
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


class Connection:
    pass


class Structure:
    pass


class Meta:
    pass
