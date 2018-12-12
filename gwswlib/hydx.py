# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)


class Hydx:
    def __init__(self):
        self.connection_nodes = []


class ConnectionNode:
    FIELDS = [
        {
            "csvheader": "UNI_IDE",
            "fieldname": "HydxIdentificatieKnooppuntOfVerbinding",
            "unit": "-",
            # "type": (str, 10),
            "required": True,
        },
        {
            "csvheader": "RST_IDE",
            "fieldname": "HydxIdentificatieRioolstelsel",
            "unit": "-",
            # "type": (str, 30),
            "required": False,
        },
        {
            "csvheader": "PUT_IDE",
            "fieldname": "HydxIdentificatieRioolput",
            "unit": "-",
            # "type": (str, 10),
            "required": True,
        },
        {
            "csvheader": "KNP_XCO",
            "fieldname": "HydxX_coordinaat",
            "unit": "m",
            # "type": (float, 12.2),
            "required": True,
        },
        {
            "csvheader": "KNP_YCO",
            "fieldname": "HydxY_coordinaat",
            "unit": "m",
            # "type": (float, 12.2),
            "required": True,
        },
        {
            "csvheader": "CMP_IDE",
            "fieldname": "HydxIdentificatieCompartiment",
            "unit": "-",
            # "type": (str, 10),
            "required": False,
        },
        {
            "csvheader": "MVD_NIV",
            "fieldname": "HydxNiveauMaaiveld",
            "unit": "m",
            # "type": (float, 8.2),
            "required": True,
        },
        {
            "csvheader": "MVD_SCH",
            "fieldname": "HydxMaaiveldschematisering",
            "unit": "-",
            # "type": (MaaiveldschematiseringColl, 3),
            "required": True,
        },
        {
            "csvheader": "WOS_OPP",
            "fieldname": "HydxOppervlakWaterOpStraat",
            "unit": "m2",
            # "type": (float, 8.2),
            "required": False,
        },
        {
            "csvheader": "KNP_MAT",
            "fieldname": "HydxMateriaalPut",
            "unit": "-",
            # "type": (MateriaalHydxColl, 3),
            "required": True,
        },
        {
            "csvheader": "KNP_VRM",
            "fieldname": "HydxVormPut",
            "unit": "-",
            # "type": (VormPutColl, 3),
            "required": True,
        },
        {
            "csvheader": "KNP_BOK",
            "fieldname": "HydxNiveauBinnenonderkantPut",
            "unit": "m",
            # "type": (float, 8.2),
            "required": True,
        },
        {
            "csvheader": "KNP_BRE",
            "fieldname": "HydxBreedte_diameterPutbodem",
            "unit": "mm",
            # "type": (float, 8),
            "required": True,
        },
        {
            "csvheader": "KNP_LEN",
            "fieldname": "HydxLengtePutbodem",
            "unit": "mm",
            # "type": (float, 8),
            "required": False,
        },
        {
            "csvheader": "KNP_TYP",
            "fieldname": "HydxTypeKnooppunt",
            "unit": "-",
            # "type": (TypeKnooppuntColl, 3),
            "required": True,
        },
        {
            "csvheader": "INI_NIV",
            "fieldname": "HydxInitieleWaterstand",
            "unit": "m",
            # "type": (float, 8.2),
            "required": False,
        },
        {
            "csvheader": "STA_OBJ",
            "fieldname": "HydxStatusObject",
            "unit": "-",
            # "type": (StatusObjectColl, 3),
            "required": False,
        },
        {
            "csvheader": "AAN_MVD",
            "fieldname": "HydxAannameMaaiveldhoogte",
            "unit": "-",
            # "type": (AannameHydXColl, 3),
            "required": False,
        },
        {
            "csvheader": "ITO_IDE",
            "fieldname": "HydxIdentificatieDefinitieIT_object",
            "unit": "-",
            # "type": (str, 10),
            "required": False,
        },
        {
            "csvheader": "ALG_TOE",
            "fieldname": "HydxToelichtingRegel",
            "unit": "-",
            # "type": (str, 100),
            "required": False,
        },
    ]

    @classmethod
    def csvheaders(cls):
        return [field["csvheader"] for field in cls.FIELDS]

    def __init__(self, codes):
        #self.uni_ide = uni_ide
        pass

    def check(self):
        pass


class Connection:
    pass


class Structure:
    pass


class Meta:
    pass
