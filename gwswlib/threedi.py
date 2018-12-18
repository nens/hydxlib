# -*- coding: utf-8 -*-
import logging

from gwswlib.sql_models.constants import Constants

# from gwswlib.sql_models.constants import Constants


logger = logging.getLogger(__name__)


MANHOLE_SHAPE_MAPPING = {
    "RND": Constants.MANHOLE_SHAPE_ROUND,
    "RHK": Constants.MANHOLE_SHAPE_RECTANGLE,
}

# skipping "VRL"
CALCULATION_TYPE_MAPPING = {
    "KNV": Constants.CALCULATION_TYPE_ISOLATED,
    "RES": Constants.CALCULATION_TYPE_CONNECTED,
}

MATERIAL_MAPPING = {
    None: None,
    "": None,
    "BET": Constants.MATERIAL_TYPE_CONCRETE,
    "PVC": Constants.MATERIAL_TYPE_PVC,
    "GRE": Constants.MATERIAL_TYPE_STONEWARE,
    "GIJ": Constants.MATERIAL_TYPE_CAST_IRON,
    "MSW": Constants.MATERIAL_TYPE_BRICKWORK,
    "HPE": Constants.MATERIAL_TYPE_HPE,
    "PIJ": Constants.MATERIAL_TYPE_SHEET_IRON,
    "STL": Constants.MATERIAL_TYPE_STEEL,
}

# skipping "CMP" and "ITP"
MANHOLE_INDICATOR_MAPPING = {
    "INS": Constants.MANHOLE_INDICATOR_MANHOLE,
    "UIT": Constants.MANHOLE_INDICATOR_OUTLET,
}


class Threedi:
    def __init__(self):
        pass

    def __repr__(self):
        pass

    def import_hydx(self, hydx):
        self.connection_nodes = []
        self.manholes = []

        for connection_node in hydx.connection_nodes:
            self.parse_connection_node(connection_node)

    def parse_connection_node(self, hydx_connection_node):
        """ parse hydx.connection_node into threedi.connection_node and threedi.manhole

        :param connection_node:
        :return:
        """

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
            "shape": self.get_manhole_shape(
                hydx_connection_node.vormput, hydx_connection_node.identificatierioolput
            ),
            "bottom_level": hydx_connection_node.niveaubinnenonderkantput,
            "material": self.get_material_type(
                hydx_connection_node.materiaalput,
                hydx_connection_node.identificatierioolput,
            ),
            "calculation_type": self.get_calculation_type(
                hydx_connection_node.materiaalput,
                hydx_connection_node.identificatierioolput,
            ),
            "manhole_indicator": self.get_manhole_indicator(
                hydx_connection_node.typeknooppunt,
                hydx_connection_node.identificatierioolput,
            ),
        }

        self.manholes.append(manhole)

    def get_manhole_shape(self, shape_code, record_code):
        try:
            return MANHOLE_SHAPE_MAPPING[shape_code]
        except KeyError:
            logging.warning(
                'Unknown "Putvorm" in gwsw record - shape code %s for record with code %s',
                shape_code,
                record_code,
            )
            return None

    def get_material_type(self, material_code, record_code):
        try:
            return MATERIAL_MAPPING[material_code]
        except KeyError:
            logging.warning(
                'Unknown "Materiaal" in gwsw record - material code %s for record with code %s',
                material_code,
                record_code,
            )
            return None

    def get_calculation_type(self, calculation_type_code, record_code):
        try:
            return CALCULATION_TYPE_MAPPING[calculation_type_code]
        except KeyError:
            logging.warning(
                'Unknown "Maaiveldschematisering" in gwsw record - calculation type code %s for record with code %s',
                calculation_type_code,
                record_code,
            )
            return None

    def get_manhole_indicator(self, manhole_indicator_code, record_code):
        try:
            return MANHOLE_INDICATOR_MAPPING[manhole_indicator_code]
        except KeyError:
            logging.warning(
                'Unknown "Type knooppunt" in gwsw record - manhole indicator code %s for record with code %s',
                manhole_indicator_code,
                record_code,
            )
            return None


def point(x, y, srid_input=28992):

    return x, y, srid_input
