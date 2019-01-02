# -*- coding: utf-8 -*-
import logging
from collections import Counter

logger = logging.getLogger(__name__)


class Hydx:
    def __init__(self):
        self.connection_nodes = []
        self.connections = []
        self.structures = []

    def import_csvline(self, line, csvfilename):

        if csvfilename == "Knooppunt1.csv":
            hydxelement = ConnectionNode()
            hydxelement.import_csvline(csvline=line)
            self.connection_nodes.append(hydxelement)
        elif csvfilename == "Verbinding1.csv":
            hydxelement = Connection()
            hydxelement.import_csvline(csvline=line)
            print(hydxelement)
            self.connections.append(hydxelement)
        elif csvfilename == "Kunstwerk1.csv":
            hydxelement = Structure()
            hydxelement.import_csvline(csvline=line)
            self.structures.append(hydxelement)

    def csvheaders(csvfilename):
        if csvfilename == "Knooppunt1.csv":
            hydxelement = ConnectionNode()
        elif csvfilename == "Verbinding1.csv":
            hydxelement = Connection()
        elif csvfilename == "Kunstwerk1.csv":
            hydxelement = Structure()
        else:
            logger.warning(
                "Headers of the following file could not be checked: %s", csvfilename
            )
            return

        return hydxelement.csvheaders()

    def check_import_data(self):
        self._check_on_unique(
            self.connection_nodes, "identificatieknooppuntofverbinding"
        )
        self._check_on_unique(self.connections, "identificatieknooppuntofverbinding")
        self._check_on_unique(self.structures, "identificatieknooppuntofverbinding")

    def _check_on_unique(self, records, unique_field, remove_double=False):
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


class Generic:
    @classmethod
    def csvheaders(cls):
        return [field["csvheader"] for field in cls.FIELDS]

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


class ConnectionNode(Generic):
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

    def __init__(self):
        pass

    def __repr__(self):
        return "<ConnectionNode %s>" % getattr(self, "identificatierioolput", None)


class Connection(Generic):
    FIELDS = [
        {
            "csvheader": "UNI_IDE",
            "fieldname": "IdentificatieKnooppuntOfVerbinding",
            "type": str,
            "required": True,
        },
        {
            "csvheader": "KN1_IDE",
            "fieldname": "IdentificatieKnooppunt1",
            "type": str,
            "required": True,
        },
        {
            "csvheader": "KN2_IDE",
            "fieldname": "IdentificatieKnooppunt2",
            "type": str,
            "required": True,
        },
        {
            "csvheader": "VRB_TYP",
            "fieldname": "TypeVerbinding",
            "type": str,
            "required": True,
        },
        {
            "csvheader": "LEI_IDE",
            "fieldname": "IdentificatieLeiding",
            "type": str,
            "required": False,
        },
        {
            "csvheader": "BOB_KN1",
            "fieldname": "BobKnooppunt1",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "BOB_KN2",
            "fieldname": "BobKnooppunt2",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "STR_RCH",
            "fieldname": "Stromingsrichting",
            "type": str,
            "required": False,
        },
        {
            "csvheader": "VRB_LEN",
            "fieldname": "LengteVerbinding",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "INZ_TYP",
            "fieldname": "TypeInzameling",
            "type": str,
            "required": False,
        },
        {
            "csvheader": "INV_KN1",
            "fieldname": "InstroomverliescoefficientKnooppunt1",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "UTV_KN1",
            "fieldname": "UitstroomverliescoefficientKnooppunt1",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "INV_KN2",
            "fieldname": "InstroomverliescoefficientKnooppunt2",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "UTV_KN2",
            "fieldname": "UitstroomverliescoefficientKnooppunt2",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "ITO_IDE",
            "fieldname": "IdentificatieDefinitieIT_object",
            "type": str,
            "required": False,
        },
        {
            "csvheader": "PRO_IDE",
            "fieldname": "IdentificatieProfieldefinitie",
            "type": str,
            "required": False,
        },
        {
            "csvheader": "STA_OBJ",
            "fieldname": "StatusObject",
            "type": str,
            "required": False,
        },
        {
            "csvheader": "AAN_BB1",
            "fieldname": "AannameBobKnooppunt1",
            "type": str,
            "required": False,
        },
        {
            "csvheader": "AAN_BB2",
            "fieldname": "AannameBobKnooppunt2",
            "type": str,
            "required": False,
        },
        {
            "csvheader": "INI_NIV",
            "fieldname": "InitieleWaterstand",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "ALG_TOE",
            "fieldname": "ToelichtingRegel",
            "type": str,
            "required": False,
        },
    ]

    def __init__(self):
        pass

    def __repr__(self):
        return "<Connection %s: %s>" % (
            getattr(self, "typeverbinding", None),
            getattr(self, "identificatieknooppuntofverbinding", None),
        )


class Structure(Generic):
    FIELDS = [
        {
            "csvheader": "UNI_IDE",
            "fieldname": "IdentificatieKnooppuntOfVerbinding",
            "type": str,
            "required": True,
        },
        {
            "csvheader": "KWK_TYP",
            "fieldname": "TypeKunstwerk",
            "type": str,
            "required": True,
        },
        {
            "csvheader": "BWS_NIV",
            "fieldname": "Buitenwaterstand",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "PRO_BOK",
            "fieldname": "NiveauBinnenonderkantProfiel",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "DRL_COE",
            "fieldname": "ContractiecoefficientDoorlaatprofiel",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "DRL_CAP",
            "fieldname": "MaximaleCapaciteitDoorlaat",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "OVS_BRE",
            "fieldname": "BreedteOverstortdrempel",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "OVS_NIV",
            "fieldname": "NiveauOverstortdrempel",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "OVS_VOH",
            "fieldname": "VrijeOverstorthoogte",
            "type": str,
            "required": False,
        },
        {
            "csvheader": "OVS_COE",
            "fieldname": "AfvoercoefficientOverstortdrempel",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "PMP_CAP",
            "fieldname": "Pompcapaciteit",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "PMP_AN1",
            "fieldname": "AanslagniveauBenedenstrooms",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "PMP_AF1",
            "fieldname": "AfslagniveauBenedenstrooms",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "PMP_AN2",
            "fieldname": "AanslagniveauBovenstrooms",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "PMP_AF2",
            "fieldname": "AfslagniveauBovenstrooms",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "QDH_NIV",
            "fieldname": "NiveauverschilDebiet_verhangrelatie",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "QDH_DEB",
            "fieldname": "DebietverschilDebiet_verhangrelatie",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "AAN_OVN",
            "fieldname": "AannameNiveauOverstortdrempel",
            "type": str,
            "required": False,
        },
        {
            "csvheader": "AAN_OVB",
            "fieldname": "AannameBreedteOverstortdrempel",
            "type": str,
            "required": False,
        },
        {
            "csvheader": "AAN_CAP",
            "fieldname": "AannamePompcapaciteitPomp",
            "type": str,
            "required": False,
        },
        {
            "csvheader": "AAN_ANS",
            "fieldname": "AannameAanslagniveauPomp",
            "type": str,
            "required": False,
        },
        {
            "csvheader": "AAN_AFS",
            "fieldname": "AannameAfslagniveauPomp",
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

    def __init__(self):
        pass

    def __repr__(self):
        return "<Structure %s: %s>" % (
            getattr(self, "typekunstwerk", None),
            getattr(self, "identificatieknooppuntofverbinding", None),
        )


class Meta:
    pass
