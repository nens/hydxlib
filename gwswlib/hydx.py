# -*- coding: utf-8 -*-
import logging
from collections import Counter

logger = logging.getLogger(__name__)


class Generic:
    FIELDS = []

    @classmethod
    def csvheaders(cls):
        return [field["csvheader"] for field in cls.FIELDS]

    @classmethod
    def import_csvline(cls, csvline):
        # AV - function looks like hydroObjectListFromSUFHYD in turtleurbanclasses.py
        instance = cls()

        for field in cls.FIELDS:
            fieldname = field["fieldname"].lower()
            value = csvline[field["csvheader"]]
            datatype = field["type"]

            # set fields to defined data type and load into object
            if value is None or value == "":
                setattr(instance, fieldname, None)
            elif datatype == float and not check_string_to_float(value):
                setattr(instance, fieldname, None)
                logger.error(
                    "%s in %s does not contain a float: %r", fieldname, instance, value
                )
            else:
                setattr(instance, fieldname, datatype(value))
        return instance

    def __str__(self):
        return self.__repr__().strip("<>")


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


class Profile(Generic):
    FIELDS = [
        {
            "csvheader": "PRO_IDE",
            "fieldname": "IdentificatieProfieldefinitie",
            "type": str,
            "required": True,
        },
        {
            "csvheader": "PRO_MAT",
            "fieldname": "Materiaal",
            "type": str,
            "required": False,
        },
        {
            "csvheader": "PRO_VRM",
            "fieldname": "VormProfiel",
            "type": str,
            "required": False,
        },
        {
            "csvheader": "PRO_BRE",
            "fieldname": "Breedte_diameterProfiel",
            "type": str,
            "required": False,
        },
        {
            "csvheader": "PRO_HGT",
            "fieldname": "HoogteProfiel",
            "type": str,
            "required": False,
        },
        {
            "csvheader": "OPL_HL1",
            "fieldname": "Co_tangensHelling1",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "OPL_HL2",
            "fieldname": "Co_tangensHelling2",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "PRO_NIV",
            "fieldname": "NiveauBovenBob",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "PRO_NOP",
            "fieldname": "NatOppervlakNiveau",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "PRO_NOM",
            "fieldname": "NatteOmtrekNiveau",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "PRO_BRN",
            "fieldname": "BreedteNiveau",
            "type": float,
            "required": False,
        },
        {
            "csvheader": "AAN_PBR",
            "fieldname": "AannameProfielbreedte",
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
        return "<Profile %s>" % (getattr(self, "identificatieprofieldefinitie", None),)


class Meta:
    pass


class Hydx:
    CSVFILES = {
        "Knooppunt1.csv": {
            "hydx_class": ConnectionNode,
            "collection_name": "connection_nodes",
        },
        "Kunstwerk1.csv": {"hydx_class": Structure, "collection_name": "structures"},
        "Verbinding1.csv": {"hydx_class": Connection, "collection_name": "connections"},
        "Profiel1.csv": {"hydx_class": Profile, "collection_name": "profiles"},
    }

    def __init__(self):
        self.connection_nodes = []
        self.connections = []
        self.structures = []
        self.profiles = []

    def import_csvfile(self, csvreader, csvfilename):

        csvfile_information = self.CSVFILES[csvfilename]
        check_headers(
            csvreader.fieldnames, csvfile_information["hydx_class"].csvheaders()
        )

        for line in csvreader:
            hydx_class = csvfile_information["hydx_class"]
            hydxelement = hydx_class.import_csvline(csvline=line)
            collection = getattr(self, csvfile_information["collection_name"])
            collection.append(hydxelement)

    def check_import_data(self):
        self._check_on_unique(
            self.connection_nodes, "identificatieknooppuntofverbinding"
        )
        self._check_on_unique(self.connections, "identificatieknooppuntofverbinding")
        self._check_on_unique(self.structures, "identificatieknooppuntofverbinding")
        self._check_on_unique(self.profiles, "identificatieprofieldefinitie")

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


def check_headers(found, expected):
    """Compares two header columns on extra or missing ones"""
    extra_columns = set(found) - set(expected)
    missing_columns = set(expected) - set(found)
    if extra_columns:
        logger.warning("extra columns found: %s", extra_columns)

    if missing_columns:
        logger.error("missing columns found: %s", missing_columns)


def check_string_to_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
