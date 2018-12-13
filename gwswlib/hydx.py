# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)


class Hydx:
    def __init__(self):
        self.connection_nodes = []


class ConnectionNode:
    MAAIVELDSCHEMATISERINGCOLL = [
        {"Label": "Reservoir", "Code": "RES"},
        {"Label": "Gekneveld", "Code": "KNV"},
        {"Label": "Verlies", "Code": "VRL"},
    ]

    MATERIAALHYDXCOLL = [
        {"Label": "Beton", "Code": "BET"},
        {"Label": "Gewapend beton", "Code": "BET"},
        {"Label": "Polyvinylchloride", "Code": "PVC"},
        {"Label": "Gres", "Code": "GRE"},
        {"Label": "Gietijzer", "Code": "GIJ"},
        {"Label": "Metselwerk", "Code": "MSW"},
        {"Label": "Metselwerk (baksteen)", "Code": "MSW"},
        {"Label": "Metselwerk (bepleisterd)", "Code": "MSW"},
        {"Label": "Metselwerk (onbepleisterd)", "Code": "MSW"},
        {"Label": "HDPE", "Code": "HPE"},
        {"Label": "Polyester", "Code": "HPE"},
        {"Label": "Polyetheen", "Code": "HPE"},
        {"Label": "Polypropyleen", "Code": "HPE"},
        {"Label": "Plaatijzer", "Code": "PIJ"},
        {"Label": "Staal", "Code": "STL"},
    ]

    VORMPUTCOLL = [
        {"Label": "Rechthoekig", "Code": "RHK"},
        {"Label": "Rond", "Code": "RND"},
    ]

    TYPEKNOOPPUNTCOLL = [
        {"Label": "Inspectieput", "Code": "INS"},
        {"Label": "Infiltratieput", "Code": "ITP"},
        {"Label": "Compartiment", "Code": "CMP"},
        {"Label": "Uitlaat", "Code": "UIT"},
    ]

    STATUSOBJECTCOLL = [
        {"Label": "In gebruik", "Code": "ACT"},
        {"Label": "In ontwerp", "Code": "ONT"},
    ]

    AANNAMEHYDXCOLL = [
        {"Label": "Expert judgement", "Code": "EXJ"},
        {"Label": "Conform ontwerp", "Code": "ONT"},
        {"Label": "Conform norm", "Code": "NRM"},
    ]

    FIELDS = [
        {
            "csvheader": "UNI_IDE",
            "fieldname": "HydxIdentificatieKnooppuntOfVerbinding",
            "unit": "-",
            "type": ('string', 10),
            "required": True,
        },
        {
            "csvheader": "RST_IDE",
            "fieldname": "HydxIdentificatieRioolstelsel",
            "unit": "-",
            "type": ('string', 30),
            "required": False,
        },
        {
            "csvheader": "PUT_IDE",
            "fieldname": "HydxIdentificatieRioolput",
            "unit": "-",
            "type": ('string', 10),
            "required": True,
        },
        {
            "csvheader": "KNP_XCO",
            "fieldname": "HydxX_coordinaat",
            "unit": "m",
            "type": ('float', 12.2),
            "required": True,
        },
        {
            "csvheader": "KNP_YCO",
            "fieldname": "HydxY_coordinaat",
            "unit": "m",
            "type": ('float', 12.2),
            "required": True,
        },
        {
            "csvheader": "CMP_IDE",
            "fieldname": "HydxIdentificatieCompartiment",
            "unit": "-",
            "type": ('string', 10),
            "required": False,
        },
        {
            "csvheader": "MVD_NIV",
            "fieldname": "HydxNiveauMaaiveld",
            "unit": "m",
            "type": ('float', 8.2),
            "required": True,
        },
        {
            "csvheader": "MVD_SCH",
            "fieldname": "HydxMaaiveldschematisering",
            "unit": "-",
            "type": ('string', 3),
            "required": True,
        },
        {
            "csvheader": "WOS_OPP",
            "fieldname": "HydxOppervlakWaterOpStraat",
            "unit": "m2",
            "type": ('float', 8.2),
            "required": False,
        },
        {
            "csvheader": "KNP_MAT",
            "fieldname": "HydxMateriaalPut",
            "unit": "-",
            "type": ('string', 3),
            "required": True,
        },
        {
            "csvheader": "KNP_VRM",
            "fieldname": "HydxVormPut",
            "unit": "-",
            "type": ('string', 3),
            "required": True,
        },
        {
            "csvheader": "KNP_BOK",
            "fieldname": "HydxNiveauBinnenonderkantPut",
            "unit": "m",
            "type": ('float', 8.2),
            "required": True,
        },
        {
            "csvheader": "KNP_BRE",
            "fieldname": "HydxBreedte_diameterPutbodem",
            "unit": "mm",
            "type": ('float', 8),
            "required": True,
        },
        {
            "csvheader": "KNP_LEN",
            "fieldname": "HydxLengtePutbodem",
            "unit": "mm",
            "type": ('float', 8),
            "required": False,
        },
        {
            "csvheader": "KNP_TYP",
            "fieldname": "HydxTypeKnooppunt",
            "unit": "-",
            "type": ('string', 3),
            "required": True,
        },
        {
            "csvheader": "INI_NIV",
            "fieldname": "HydxInitieleWaterstand",
            "unit": "m",
            "type": ('float', 8.2),
            "required": False,
        },
        {
            "csvheader": "STA_OBJ",
            "fieldname": "HydxStatusObject",
            "unit": "-",
            "type": ('string', 3),
            "required": False,
        },
        {
            "csvheader": "AAN_MVD",
            "fieldname": "HydxAannameMaaiveldhoogte",
            "unit": "-",
            "type": ('string', 3),
            "required": False,
        },
        {
            "csvheader": "ITO_IDE",
            "fieldname": "HydxIdentificatieDefinitieIT_object",
            "unit": "-",
            "type": ('string', 10),
            "required": False,
        },
        {
            "csvheader": "ALG_TOE",
            "fieldname": "HydxToelichtingRegel",
            "unit": "-",
            "type": ('string', 100),
            "required": False,
        },
    ]

    @classmethod
    def csvheaders(cls):
        return [field["csvheader"] for field in cls.FIELDS]

    @classmethod
    def fields(cls):
        return cls.FIELDS

    def __init__(self, codes):
        self.node = {}
        FIELDS = self.fields()
        for field in self.fields():
            
            # set empty values to None
            if codes[field["csvheader"]] == '':
                codes[field["csvheader"]] = None

            # set fields to defined data type and load into object
            if field["type"][0] == "string" and codes[field["csvheader"]] is not None:
                self.node[field["csvheader"]] = str(codes[field["csvheader"]])
            elif field["type"][0] == "float" and codes[field["csvheader"]] is not None:
                self.node[field["csvheader"]] = float(codes[field["csvheader"]])
            else:
                self.node[field["csvheader"]] = None
        pass

    def check(self):
        pass


class Connection:
    pass


class Structure:
    pass


class Meta:
    pass
