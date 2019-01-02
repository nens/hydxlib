# -*- coding: utf-8 -*-
import logging

from gwswlib.sql_models.constants import Constants


logger = logging.getLogger(__name__)

MAPPING = {"MANHOLE_SHAPE_MAPPING": "Putvorm"}

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

        for connection_node in hydx.connection_nodes:
            check_if_element_is_created_twice(
                connection_node.identificatieknooppuntofverbinding,
                self.connection_nodes,
                "Connection node",
            )
            self.add_connection_node(connection_node)

        for connection in hydx.connections:
            check_if_element_is_created_twice(
                connection.identificatieknooppuntofverbinding,
                self.connections,
                "Connection",
            )

            if connection.typeverbinding in ["GSL", "OPL", "ITR"]:
                logger.warning(
                    'The following "typeverbinding" is not connected in this importer: %s',
                    connection.typeverbinding,
                )
            elif connection.typeverbinding in ["PMP", "OVS", "DRL"]:
                linkedstructures = [
                    structure
                    for structure in hydx.structures
                    if structure.identificatieknooppuntofverbinding
                    == connection.identificatieknooppuntofverbinding
                ]
                if len(linkedstructures) != 1:
                    logging.error(
                        "Only first structure is created for structures with double values %r",
                        connection.identificatieknooppuntofverbinding,
                    )
                self.add_structure(connection, linkedstructures[0])
            else:
                logger.warning(
                    'The following "typeverbinding" is not recognized: %s',
                    connection.typeverbinding,
                )

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

    def add_structure(self, hydx_connection, hydx_structure):
        """Add hydx.structure and hydx.connection into threedi.pumpstation"""

        element_codes, element_display_names = self.get_code(
            hydx_connection.identificatieknooppunt1,
            hydx_connection.identificatieknooppunt2,
        )

        if hydx_structure.typekunstwerk == "PMP":
            if hydx_structure.aanslagniveaubovenstrooms is not None:
                pumpstation_type = 2
                pumpstation_start_level = hydx_structure.aanslagniveaubovenstrooms
                pumpstation_stop_level = hydx_structure.afslagniveaubovenstrooms
            else:
                pumpstation_type = 1
                pumpstation_start_level = hydx_structure.aanslagniveaubenedenstrooms
                pumpstation_stop_level = hydx_structure.afslagniveaubenedenstrooms

            pumpstation = {
                "code": element_codes,
                "display_name": element_display_names,
                "start_node.code": hydx_connection.identificatieknooppunt1,
                "end_node.code": hydx_connection.identificatieknooppunt2,
                "type": pumpstation_type,
                "start_level": pumpstation_start_level,
                "lower_stop_level": pumpstation_stop_level,
                # upper_stop_level is not supported by hydx
                "upper_stop_level": None,
                "capacity": round(float(hydx_structure.pompcapaciteit) / 3.6, 5),
                "sewerage": True,
            }
            self.pumpstations.append(pumpstation)

    def get_mapping_value(self, mapping, hydx_value, record_code, name_for_logging):
        if hydx_value in mapping:
            return mapping[hydx_value]
        else:
            logging.warning(
                "Unknown %s: %s (code %r)", name_for_logging, hydx_value, record_code
            )
            return None

    def get_code(self, code1, code2=None, default_code=""):
        """
        Args:
            code1(string): object code
            code2(string): object code 2
            default_code: returned value when code is None or ''

        Returns:
            (string): combined area code
        """
        if code1 is None or code1 == "":
            code1 = default_code
        if code2 is None or code2 == "":
            code2 = default_code
        element_codes = code1 + "-" + code2

        display_name1 = [
            element["display_name"]
            for element in self.manholes
            if element["code"] == code1
        ][0]
        display_name2 = [
            element["display_name"]
            for element in self.manholes
            if element["code"] == code2
        ][0]

        if display_name1 is None or display_name1 == "":
            display_name1 = default_code
        if display_name2 is None or display_name2 == "":
            display_name2 = default_code
        element_display_names = display_name1 + "-" + display_name2

        all_connections = self.pumpstations + self.weirs + self.orifices
        nr_connections = [
            element
            for element in all_connections
            if element["code"].rpartition("-")[0] == element_codes
        ]
        connection_number = len(nr_connections) + 1

        element_codes += "-" + str(connection_number)
        element_display_names += "-" + str(connection_number)

        return element_codes, element_display_names


def point(x, y, srid_input=28992):

    return x, y, srid_input


def check_if_element_is_created_twice(checked_element, created_elements, element_type):
    added_elements = [element["code"] for element in created_elements]
    if checked_element in added_elements:
        logger.error("%s is created twice with code %r", element_type, checked_element)
