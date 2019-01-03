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
                        "Only first structure is used to create a structure for connection %r",
                        connection.identificatieknooppuntofverbinding,
                    )

                if len(linkedstructures) == 0:
                    logging.error(
                        "Structure does not exist for connection %r",
                        connection.identificatieknooppuntofverbinding,
                    )
                else:
                    self.add_structure(connection, linkedstructures[0])
            else:
                logger.warning(
                    'The following "typeverbinding" is not recognized by 3Di exporter: %s',
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

        self.check_if_nodes_of_connection_exists(hydx_connection)
        element_display_names = self.get_connection_display_name_from_manholes(
            hydx_connection
        )

        if hydx_structure.typekunstwerk == "PMP":
            self.add_pumpstation(hydx_connection, hydx_structure, element_display_names)
        elif hydx_structure.typekunstwerk == "OVS":
            self.add_weir(hydx_connection, hydx_structure, element_display_names)

    def add_pumpstation(self, hydx_connection, hydx_structure, element_display_names):
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
            "display_name": element_display_names,
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

    def add_weir(self, hydx_connection, hydx_structure, element_display_names):

        waterlevel_boundary = getattr(hydx_structure, "buitenwaterstand", None)

        if waterlevel_boundary is not None:
            timeseries = "0,{0}\n9999,{0} ".format(waterlevel_boundary)
        else:
            timeseries = None

        if hydx_connection.stromingsrichting not in ["GSL", "1_2", "2_1", "OPN"]:
            logger.warning(
                'Flow direction is not recognized for %r with record %r, "OPN" is assumed',
                hydx_connection.typeverbinding,
                hydx_connection.identificatieknooppuntofverbinding,
            )

        if (
            hydx_connection.stromingsrichting == "GSL"
            or hydx_connection.stromingsrichting == "2_1"
        ):
            discharge_coefficient_positive = 0
        else:
            discharge_coefficient_positive = (
                hydx_structure.afvoercoefficientoverstortdrempel
            )
        if (
            hydx_connection.stromingsrichting == "GSL"
            or hydx_connection.stromingsrichting == "1_2"
        ):
            discharge_coefficient_negative = 0
        else:
            discharge_coefficient_negative = (
                hydx_structure.afvoercoefficientoverstortdrempel
            )
        weir = {
            "code": hydx_connection.identificatieknooppuntofverbinding,
            "display_name": element_display_names,
            "start_node.code": hydx_connection.identificatieknooppunt1,
            "end_node.code": hydx_connection.identificatieknooppunt2,
            "cross_section_details": {
                "shape": Constants.SHAPE_RECTANGLE,
                "width": hydx_structure.breedteoverstortdrempel,
                "height": None,
            },
            "crest_type": Constants.CREST_TYPE_SHARP_CRESTED,
            "crest_level": hydx_structure.niveauoverstortdrempel,
            "discharge_coefficient_positive": discharge_coefficient_positive,
            "discharge_coefficient_negative": discharge_coefficient_negative,
            "sewerage": True,
            "boundary_details": {
                "timeseries": timeseries,
                "boundary_type": Constants.BOUNDARY_TYPE_WATERLEVEL,
            },
        }

        self.weirs.append(weir)

    def get_mapping_value(self, mapping, hydx_value, record_code, name_for_logging):
        if hydx_value in mapping:
            return mapping[hydx_value]
        else:
            logging.warning(
                "Unknown %s: %s (code %r)", name_for_logging, hydx_value, record_code
            )
            return None

    def check_if_nodes_of_connection_exists(self, connection, default_code=""):
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

    def get_connection_display_name_from_manholes(self, connection, default_code=""):
        code1 = connection.identificatieknooppunt1
        code2 = connection.identificatieknooppunt2

        if code1 is None or code1 == "":
            code1 = default_code
        if code2 is None or code2 == "":
            code2 = default_code

        manh_dict = {
            manhole["code"]: manhole["display_name"] for manhole in self.manholes
        }
        if code1 in manh_dict:
            display_name1 = manh_dict[code1]
        else:
            display_name1 = default_code

        if code2 in manh_dict:
            display_name2 = manh_dict[code2]
        else:
            display_name2 = default_code
        element_display_names = display_name1 + "-" + display_name2
        element_codes = code1 + "-" + code2

        all_connections = self.pumpstations + self.weirs + self.orifices
        nr_connections = [
            element
            for element in all_connections
            if element["code"].rpartition("-")[0] == element_codes
        ]
        connection_number = len(nr_connections) + 1

        element_display_names += "-" + str(connection_number)

        return element_display_names


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
