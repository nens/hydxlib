# -*- coding: utf-8 -*-
import logging
from collections import OrderedDict

from hydxlib.sql_models.constants import Constants
from hydxlib.hydx import Profile


logger = logging.getLogger(__name__)

MANHOLE_SHAPE_MAPPING = {
    "RND": Constants.MANHOLE_SHAPE_ROUND,
    "RHK": Constants.MANHOLE_SHAPE_RECTANGLE,
}

# for now skipping "VRL"
CALCULATION_TYPE_MAPPING = {
    "KNV": Constants.CALCULATION_TYPE_ISOLATED,
    "RES": Constants.CALCULATION_TYPE_CONNECTED,
}

MATERIAL_MAPPING = {
    "BET": Constants.MATERIAL_TYPE_CONCRETE,
    "PVC": Constants.MATERIAL_TYPE_PVC,
    "GRE": Constants.MATERIAL_TYPE_STONEWARE,
    "GIJ": Constants.MATERIAL_TYPE_CAST_IRON,
    "MSW": Constants.MATERIAL_TYPE_BRICKWORK,
    "HPE": Constants.MATERIAL_TYPE_HPE,
    "PIJ": Constants.MATERIAL_TYPE_SHEET_IRON,
    "STL": Constants.MATERIAL_TYPE_STEEL,
}

# for now skipping "CMP" and "ITP"
MANHOLE_INDICATOR_MAPPING = {
    "INS": Constants.MANHOLE_INDICATOR_MANHOLE,
    "UIT": Constants.MANHOLE_INDICATOR_OUTLET,
}

# for now skipping "MVR", "HEU"
SHAPE_MAPPING = {
    "RND": Constants.SHAPE_ROUND,
    "EIV": Constants.SHAPE_EGG,
    "RHK": Constants.SHAPE_TABULATED_RECTANGLE,
    "TPZ": Constants.SHAPE_TABULATED_TRAPEZIUM,
}


class Threedi:
    def __init__(self):
        pass

    def import_hydx(self, hydx):
        self.connection_nodes = []
        self.manholes = []
        self.connections = []
        self.pumpstations = []
        self.weirs = []
        self.orifices = []
        self.cross_sections = []

        for connection_node in hydx.connection_nodes:
            check_if_element_is_created_with_same_code(
                connection_node.identificatieknooppuntofverbinding,
                self.connection_nodes,
                "Connection node",
            )
            self.add_connection_node(connection_node)

        for connection in hydx.connections:
            check_if_element_is_created_with_same_code(
                connection.identificatieknooppuntofverbinding,
                self.connections,
                "Connection",
            )

            linkedprofile = None
            if connection.typeverbinding in ["GSL", "OPL", "ITR", "DRL"]:
                linkedprofiles = [
                    profile
                    for profile in hydx.profiles
                    if profile.identificatieprofieldefinitie
                    == connection.identificatieprofieldefinitie
                ]

                if len(linkedprofiles) > 1:
                    logging.error(
                        "Only first profile is used to create a profile %r for connection %r",
                        connection.identificatieprofieldefinitie,
                        connection.identificatieknooppuntofverbinding,
                    )

                if len(linkedprofiles) == 0:
                    logging.error(
                        "Profile %r does not exist for connection %r",
                        connection.identificatieprofieldefinitie,
                        connection.identificatieknooppuntofverbinding,
                    )
                else:
                    linkedprofile = linkedprofiles[0]

            if connection.typeverbinding in ["GSL", "OPL", "ITR"]:
                logger.warning(
                    'The following "typeverbinding" is not implemented in this importer: %s',
                    connection.typeverbinding,
                )
            elif connection.typeverbinding in ["PMP", "OVS", "DRL"]:
                linkedstructures = [
                    structure
                    for structure in hydx.structures
                    if structure.identificatieknooppuntofverbinding
                    == connection.identificatieknooppuntofverbinding
                ]

                if len(linkedstructures) > 1:
                    logging.error(
                        "Only first structure information is used to create a structure for connection %r",
                        connection.identificatieknooppuntofverbinding,
                    )

                if len(linkedstructures) == 0:
                    logging.error(
                        "Structure does not exist for connection %r",
                        connection.identificatieknooppuntofverbinding,
                    )
                else:
                    self.add_structure(connection, linkedstructures[0], linkedprofile)
            else:
                logger.warning(
                    'The following "typeverbinding" is not recognized by 3Di exporter: %s',
                    connection.typeverbinding,
                )

        self.generate_cross_sections()

    def add_connection_node(self, hydx_connection_node):
        """Add hydx.connection_node into threedi.connection_node and threedi.manhole"""

        # get connection_nodes attributes
        connection_node = {
            "code": hydx_connection_node.identificatieknooppuntofverbinding,
            "initial_waterlevel": hydx_connection_node.initielewaterstand,
            "geom": point(
                hydx_connection_node.x_coordinaat,
                hydx_connection_node.y_coordinaat,
                28992,
            ),
        }

        self.connection_nodes.append(connection_node)

        # get manhole attributes
        manhole = {
            "code": hydx_connection_node.identificatieknooppuntofverbinding,
            "display_name": hydx_connection_node.identificatierioolput,
            "surface_level": hydx_connection_node.niveaumaaiveld,
            "width": hydx_connection_node.breedte_diameterputbodem,
            "length": hydx_connection_node.lengteputbodem,
            "shape": self.get_mapping_value(
                MANHOLE_SHAPE_MAPPING,
                hydx_connection_node.vormput,
                hydx_connection_node.identificatierioolput,
                name_for_logging="manhole shape",
            ),
            "bottom_level": hydx_connection_node.niveaubinnenonderkantput,
            "calculation_type": self.get_mapping_value(
                CALCULATION_TYPE_MAPPING,
                hydx_connection_node.materiaalput,
                hydx_connection_node.identificatierioolput,
                name_for_logging="manhole surface schematization",
            ),
            "manhole_indicator": self.get_mapping_value(
                MANHOLE_INDICATOR_MAPPING,
                hydx_connection_node.typeknooppunt,
                hydx_connection_node.identificatierioolput,
                name_for_logging="manhole indicator",
            ),
        }

        self.manholes.append(manhole)

    def add_structure(self, hydx_connection, hydx_structure, hydx_profile=None):
        """Add hydx.structure and hydx.connection into threedi.pumpstation"""
        self.check_if_nodes_of_connection_exists(hydx_connection)
        combined_display_name_string = self.get_connection_display_names_from_manholes(
            hydx_connection
        )

        if hydx_structure.typekunstwerk == "PMP":
            self.add_pumpstation(
                hydx_connection, hydx_structure, combined_display_name_string
            )
        elif hydx_structure.typekunstwerk == "OVS":
            self.add_weir(hydx_connection, hydx_structure, combined_display_name_string)
        elif hydx_structure.typekunstwerk == "DRL":
            if hydx_profile is None:
                hydx_profile = get_hydx_default_profile()
            self.add_orifice(
                hydx_connection,
                hydx_structure,
                hydx_profile,
                combined_display_name_string,
            )

    def add_pumpstation(
        self, hydx_connection, hydx_structure, combined_display_name_string
    ):
        if hydx_structure.aanslagniveaubovenstrooms is not None:
            pumpstation_type = 2
            pumpstation_start_level = hydx_structure.aanslagniveaubovenstrooms
            pumpstation_stop_level = hydx_structure.afslagniveaubovenstrooms
        else:
            pumpstation_type = 1
            pumpstation_start_level = hydx_structure.aanslagniveaubenedenstrooms
            pumpstation_stop_level = hydx_structure.afslagniveaubenedenstrooms

        pumpstation = {
            "code": hydx_connection.identificatieknooppuntofverbinding,
            "display_name": combined_display_name_string,
            "start_node.code": hydx_connection.identificatieknooppunt1,
            "end_node.code": hydx_connection.identificatieknooppunt2,
            "type_": pumpstation_type,
            "start_level": pumpstation_start_level,
            "lower_stop_level": pumpstation_stop_level,
            # upper_stop_level is not supported by hydx
            "upper_stop_level": None,
            "capacity": round(float(hydx_structure.pompcapaciteit) / 3.6, 5),
            "sewerage": True,
        }
        self.pumpstations.append(pumpstation)

    def add_weir(self, hydx_connection, hydx_structure, combined_display_name_string):
        waterlevel_boundary = getattr(hydx_structure, "buitenwaterstand", None)
        if waterlevel_boundary is not None:
            timeseries = "0,{0}\n9999,{0} ".format(waterlevel_boundary)
        else:
            timeseries = None

        hydx_connection = self.get_discharge_coefficients(
            hydx_connection, hydx_structure
        )

        weir = {
            "code": hydx_connection.identificatieknooppuntofverbinding,
            "display_name": combined_display_name_string,
            "start_node.code": hydx_connection.identificatieknooppunt1,
            "end_node.code": hydx_connection.identificatieknooppunt2,
            "cross_section_details": {
                "shape": Constants.SHAPE_RECTANGLE,
                "width": hydx_structure.breedteoverstortdrempel,
                "height": None,
            },
            "crest_type": Constants.CREST_TYPE_SHARP_CRESTED,
            "crest_level": hydx_structure.niveauoverstortdrempel,
            "discharge_coefficient_positive": hydx_connection.discharge_coefficient_positive,
            "discharge_coefficient_negative": hydx_connection.discharge_coefficient_negative,
            "sewerage": True,
            "boundary_details": {
                "timeseries": timeseries,
                "boundary_type": Constants.BOUNDARY_TYPE_WATERLEVEL,
            },
        }
        self.weirs.append(weir)

    def add_orifice(
        self,
        hydx_connection,
        hydx_structure,
        hydx_profile,
        combined_display_name_string,
    ):

        hydx_connection = self.get_discharge_coefficients(
            hydx_connection, hydx_structure
        )

        hydx_profile.breedte_diameterprofiel = transform_unit_mm_to_m(
            hydx_profile.breedte_diameterprofiel
        )
        hydx_profile.hoogteprofiel = transform_unit_mm_to_m(hydx_profile.hoogteprofiel)

        orifice = {
            "code": hydx_connection.identificatieknooppuntofverbinding,
            "display_name": combined_display_name_string,
            "start_node.code": hydx_connection.identificatieknooppunt1,
            "end_node.code": hydx_connection.identificatieknooppunt2,
            "cross_section_details": {
                "shape": self.get_mapping_value(
                    SHAPE_MAPPING,
                    hydx_profile.vormprofiel,
                    hydx_connection.identificatieknooppuntofverbinding,
                    name_for_logging="shape of orifice",
                ),
                "width": hydx_profile.breedte_diameterprofiel,
                "height": hydx_profile.hoogteprofiel,
            },
            "discharge_coefficient_positive": hydx_connection.discharge_coefficient_positive,
            "discharge_coefficient_negative": hydx_connection.discharge_coefficient_negative,
            "sewerage": True,
            "max_capacity": hydx_structure.maximalecapaciteitdoorlaat,
            "crest_type": Constants.CREST_TYPE_SHARP_CRESTED,
            "crest_level": hydx_structure.niveaubinnenonderkantprofiel,
        }

        self.orifices.append(orifice)

    def generate_cross_sections(self):
        cross_sections = {}
        cross_sections["default"] = {
            "width": 1,
            "height": 1,
            "shape": Constants.SHAPE_ROUND,
            "code": "default",
        }

        connections_with_cross_sections = self.weirs + self.orifices
        for connection in connections_with_cross_sections:
            cross_section = connection["cross_section_details"]
            if cross_section["shape"] == Constants.SHAPE_ROUND:
                code = "round_{width}".format(**cross_section)
            elif cross_section["shape"] == Constants.SHAPE_EGG:
                code = "egg_w{width}_h{height}".format(**cross_section)
            elif cross_section["shape"] == Constants.SHAPE_RECTANGLE:
                code = "rectangle_w{width}_open".format(**cross_section)
            elif cross_section["shape"] == Constants.SHAPE_TABULATED_RECTANGLE:
                code = "rectangle_w{width}_h{height}".format(**cross_section)
                cross_section["width"] = "{0} {0} 0".format(cross_section["width"])
                cross_section["height"] = "0 {0} {0}".format(cross_section["height"])
            else:
                code = "default"
            # add unique cross_sections to cross_section definition
            if code not in cross_sections:
                cross_sections[code] = cross_section
                cross_sections[code]["code"] = code

            connection["cross_section_code"] = code

        self.cross_sections = cross_sections

    def get_mapping_value(self, mapping, hydx_value, record_code, name_for_logging):
        if hydx_value in mapping:
            return mapping[hydx_value]
        else:
            logging.warning(
                "Unknown %s: %s (code %r)", name_for_logging, hydx_value, record_code
            )
            return None

    def check_if_nodes_of_connection_exists(self, connection):
        connection_code = connection.identificatieknooppuntofverbinding
        code1 = connection.identificatieknooppunt1
        code2 = connection.identificatieknooppunt2

        manh_list = [manhole["code"] for manhole in self.manholes]
        if code1 not in manh_list:
            logging.error(
                "Start connection node %r could not be found for record %r",
                code1,
                connection_code,
            )
        if code2 not in manh_list:
            logging.error(
                "End connection node %r could not be found for record %r",
                code2,
                connection_code,
            )

    def get_connection_display_names_from_manholes(self, connection):
        code1 = connection.identificatieknooppunt1
        code2 = connection.identificatieknooppunt2
        default_code = ""

        manhole_dict = {
            manhole["code"]: manhole["display_name"] for manhole in self.manholes
        }
        display_name1 = manhole_dict.get(code1, default_code)
        display_name2 = manhole_dict.get(code2, default_code)
        combined_display_name_string = display_name1 + "-" + display_name2

        all_connections = self.pumpstations + self.weirs + self.orifices
        nr_connections = [
            element["display_name"]
            for element in all_connections
            if element["display_name"].startswith(combined_display_name_string)
        ]
        connection_number = len(nr_connections) + 1

        combined_display_name_string += "-" + str(connection_number)

        return combined_display_name_string

    def get_discharge_coefficients(self, hydx_connection, hydx_structure):
        if hydx_connection.stromingsrichting not in ["GSL", "1_2", "2_1", "OPN"]:
            hydx_connection.stromingsrichting = "OPN"
            logger.warning(
                'Flow direction is not recognized for %r with record %r, "OPN" is assumed',
                hydx_connection.typeverbinding,
                hydx_connection.identificatieknooppuntofverbinding,
            )

        if (
            hydx_connection.stromingsrichting == "GSL"
            or hydx_connection.stromingsrichting == "2_1"
        ):
            hydx_connection.discharge_coefficient_positive = 0
        elif (
            hydx_connection.stromingsrichting == "OPN"
            or hydx_connection.stromingsrichting == "1_2"
        ):
            hydx_connection.discharge_coefficient_positive = (
                hydx_structure.afvoercoefficientoverstortdrempel
            )

        if (
            hydx_connection.stromingsrichting == "GSL"
            or hydx_connection.stromingsrichting == "1_2"
        ):
            hydx_connection.discharge_coefficient_negative = 0
        elif (
            hydx_connection.stromingsrichting == "OPN"
            or hydx_connection.stromingsrichting == "2_1"
        ):
            hydx_connection.discharge_coefficient_negative = (
                hydx_structure.afvoercoefficientoverstortdrempel
            )
        return hydx_connection


def get_hydx_default_profile():
    default_profile = OrderedDict(
        [
            ("PRO_IDE", "DEFAULT"),
            ("PRO_MAT", "PVC"),
            ("PRO_VRM", "RND"),
            ("PRO_BRE", "1000"),
            ("PRO_HGT", "1000"),
            ("OPL_HL1", ""),
            ("OPL_HL2", ""),
            ("PRO_NIV", ""),
            ("PRO_NOP", ""),
            ("PRO_NOM", ""),
            ("PRO_BRN", ""),
            ("AAN_PBR", ""),
            ("ALG_TOE", "default"),
        ]
    )
    return Profile.import_csvline(csvline=default_profile)


def point(x, y, srid_input=28992):

    return x, y, srid_input


def check_if_element_is_created_with_same_code(
    checked_element, created_elements, element_type
):
    added_elements = [element["code"] for element in created_elements]
    if checked_element in added_elements:
        logger.error(
            "Multiple elements %r are created with the same code %r",
            element_type,
            checked_element,
        )


def transform_unit_mm_to_m(value_mm):
    if value_mm is not None:
        return float(value_mm) / 1000.0
    else:
        return None
