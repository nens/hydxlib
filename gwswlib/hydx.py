# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)


class Hydx:
    def __init__(self):
        self.connection_nodes = []

    def check_import_data(self):
        self._check_on_unique(self.connection_nodes, "identificatieknooppuntofverbinding", True, "knoop")

    def _check_on_unique(
        self,
        records,
        unique_field,
        remove_doubles=False,
        item_name_for_logging="",
        log_level=logging.WARNING,
    ):

        values = [m.__dict__[unique_field] for m in records]

        if len(set(values)) == len(values):
            return True, set()

        doubles = []
        value_set = set()

        for i in reversed(range(0, len(records))):
            record = records[i]
            if record.__dict__[unique_field] in value_set:
                doubles.append(record)
                logging.warning(
                    "double values in %s of %s for records with %s: %s",
                unique_field, item_name_for_logging, unique_field, record.__dict__[unique_field])

                if remove_doubles:
                    records.remove(record)
            else:
                value_set.add(record.__dict__[unique_field])

        return False, doubles


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
