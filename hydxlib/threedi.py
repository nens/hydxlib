# -*- coding: utf-8 -*-
from .hydx import Profile
from collections import OrderedDict
from enum import Enum
from threedi_modelchecker.threedi_model.constants import BoundaryType
from threedi_modelchecker.threedi_model.constants import CrestType
from threedi_modelchecker.threedi_model.constants import CrossSectionShape
from threedi_modelchecker.threedi_model.constants import PipeCalculationType
from threedi_modelchecker.threedi_model.constants import SewerageType
from threedi_modelchecker.threedi_model.constants import SurfaceClass
from threedi_modelchecker.threedi_model.constants import SurfaceInclinationType

import logging


logger = logging.getLogger(__name__)


class PipeMaterialType(Enum):
    CONCRETE = 0
    PVC = 1
    STONEWARE = 2
    CAST_IRON = 3
    BRICKWORK = 4
    HPE = 5
    HPDE = 6
    SHEET_IRON = 7
    STEEL = 8


class ManholeIndicator(Enum):
    MANHOLE = 0
    OUTLET = 1


class ManholeShape(Enum):
    RECTANGLE = "rect"
    ROUND = "rnd"


MANHOLE_SHAPE_MAPPING = {
    "RND": ManholeShape.ROUND.value,
    "RHK": ManholeShape.RECTANGLE.value,
}

# for now assuming "VRL" to be connected
CALCULATION_TYPE_MAPPING = {
    "KNV": PipeCalculationType.ISOLATED.value,
    "RES": PipeCalculationType.CONNECTED.value,
    "VRL": PipeCalculationType.CONNECTED.value,
}

MATERIAL_MAPPING = {
    "BET": PipeMaterialType.CONCRETE.value,
    "PVC": PipeMaterialType.PVC.value,
    "GRE": PipeMaterialType.STONEWARE.value,
    "GIJ": PipeMaterialType.CAST_IRON.value,
    "MSW": PipeMaterialType.BRICKWORK.value,
    "HPE": PipeMaterialType.HPE.value,
    "PIJ": PipeMaterialType.SHEET_IRON.value,
    "STL": PipeMaterialType.STEEL.value,
}
# NVT temporary (?) on transport
SEWERAGE_TYPE_MAPPING = {
    "GMD": SewerageType.MIXED.value,
    "HWA": SewerageType.RAIN_WATER.value,
    "DWA": SewerageType.DRY_WEATHER_FLOW.value,
    "NVT": SewerageType.TRANSPORT.value,
}

# for now ignoring CMP and ITP
MANHOLE_INDICATOR_MAPPING = {
    "INS": ManholeIndicator.MANHOLE.value,
    "UIT": ManholeIndicator.OUTLET.value,
    "ITP": ManholeIndicator.MANHOLE.value,
    "CMP": ManholeIndicator.MANHOLE.value,
}

SHAPE_MAPPING = {
    "RND": CrossSectionShape.CIRCLE.value,
    "EIV": CrossSectionShape.EGG.value,
    "EIG": CrossSectionShape.INVERTED_EGG.value,
    "RHK": CrossSectionShape.CLOSED_RECTANGLE.value,
    "TAB": CrossSectionShape.TABULATED_YZ.value,
    "HEU": CrossSectionShape.TABULATED_YZ.value,
    "MVR": CrossSectionShape.TABULATED_YZ.value,
    "UVR": CrossSectionShape.TABULATED_YZ.value,
    "OVA": CrossSectionShape.TABULATED_YZ.value,
    # "TPZ": CrossSectionShape.TABULATED_YZ.value, different implementation
    "YZP": CrossSectionShape.TABULATED_YZ.value,
}

DISCHARGE_COEFFICIENT_MAPPING = {
    "OVS": 0.8,  # AFVOERCOEFFICIENT_OVERSTORTDREMPEL
    "DRL": 0.8,  # CONTRATIECOEFFICIENT_DOORLAATPROFIEL
}

SURFACE_CLASS_MAPPING = {
    "GVH": SurfaceClass.GESLOTEN_VERHARDING.value,
    "OVH": SurfaceClass.OPEN_VERHARDING.value,
    "ONV": SurfaceClass.ONVERHARD.value,
    "DAK": SurfaceClass.PAND.value,
}

SURFACE_INCLINATION_MAPPING = {
    "HEL": SurfaceInclinationType.HELLEND.value,
    "VLA": SurfaceInclinationType.VLAK.value,
    "VLU": SurfaceInclinationType.UITGESTREKT.value,
}


def get_mapping_value(mapping, hydx_value, record_code, name_for_logging):
    if hydx_value is None:
        return None

    if hydx_value in mapping:
        return mapping[hydx_value]
    else:
        logger.error(
            "%s has an unknown %s: %s", record_code, name_for_logging, hydx_value
        )
        return None


def get_cross_section_details_tpz(
    hydx_profile, record_code, name_for_logging, material
):
    """https://data.gwsw.nl/?menu_item=individuals&item=../../def/1.5.2/Basis/Trapezium

    Als er geen profiel-geometrie is meegegeven geldt: de
    breedte leiding = bodembreedte, de hellingshoek aan beide
    zijden = 45 graden. De hoogte leiding bepaalt dan de bovenbreedte.

    We pick a closed profile here, optionally we open it later
    """
    if hydx_profile.tabulatedbreedte and hydx_profile.tabulatedhoogte:
        return {
            "code": hydx_profile.identificatieprofieldefinitie,
            "shape": CrossSectionShape.TABULATED_YZ.value,
            "width": hydx_profile.tabulatedbreedte,
            "height": hydx_profile.tabulatedhoogte,
            "material": material,
        }
    else:
        w = transform_unit_mm_to_m(hydx_profile.breedte_diameterprofiel)
        h = transform_unit_mm_to_m(hydx_profile.hoogteprofiel)
        if w is not None and h is not None:
            height = f"0 {h} {h}"
            width = f"{w} {w + 2 * h} 0"
        else:
            logger.error(
                "%s has an undefined %s.width: %s",
                record_code,
                name_for_logging,
                hydx_profile.vormprofiel,
            )
            width = ""
            height = ""

        return {
            "code": hydx_profile.identificatieprofieldefinitie,
            "shape": CrossSectionShape.TABULATED_TRAPEZIUM.value,
            "width": width,
            "height": height,
            "material": material,
        }


def is_closed(cross_section):
    if cross_section["shape"] == CrossSectionShape.TABULATED_YZ.value:
        if not cross_section["height"] or not cross_section["width"]:
            return None
        heights = cross_section["height"].split(" ")
        widths = cross_section["width"].split(" ")
        return heights[0] == heights[-1] and widths[0] == widths[-1]
    elif cross_section["shape"] == CrossSectionShape.TABULATED_TRAPEZIUM.value:
        heights = cross_section["height"].split(" ")
        widths = cross_section["width"].split(" ")
        return float(widths[-1]) == 0.0
    else:
        return True


def make_open(cross_section):
    """Transform a TPZ cross section from closed to open"""
    if cross_section["shape"] != CrossSectionShape.TABULATED_TRAPEZIUM.value:
        raise ValueError("Can't open a profile of type {cross_section['shape']}")
    cross_section["width"] = cross_section["width"].rsplit(" ", 1)[0]
    cross_section["height"] = cross_section["height"].rsplit(" ", 1)[0]


def get_cross_section_details(hydx_profile, record_code, name_for_logging):
    vormprofiel = hydx_profile.vormprofiel
    material = get_mapping_value(
        MATERIAL_MAPPING,
        hydx_profile.materiaal,
        record_code,
        name_for_logging=name_for_logging,
    )
    if vormprofiel in {"EIV", "RND", "RHK", "EIG"}:
        width = transform_unit_mm_to_m(hydx_profile.breedte_diameterprofiel)
        height = transform_unit_mm_to_m(hydx_profile.hoogteprofiel)
    elif vormprofiel == "TPZ":
        return get_cross_section_details_tpz(
            hydx_profile, record_code, name_for_logging, material
        )
    else:
        width = hydx_profile.tabulatedbreedte
        height = hydx_profile.tabulatedhoogte

    if not width:
        logger.error(
            "%s has an undefined %s.width: %s",
            record_code,
            name_for_logging,
            hydx_profile.vormprofiel,
        )

    shape = SHAPE_MAPPING.get(hydx_profile.vormprofiel)
    if shape is None:
        logger.error(
            "%s has an unknown %s: %s",
            record_code,
            name_for_logging,
            hydx_profile.vormprofiel,
        )

    return {
        "code": hydx_profile.identificatieprofieldefinitie,
        "shape": shape,
        "width": width,
        "height": height,
        "material": material,
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
        self.pipes = []
        self.impervious_surfaces = []
        self.impervious_surface_maps = []
        self.outlets = []
        self.cross_sections = []

        for connection_node in hydx.connection_nodes:
            check_if_element_is_created_with_same_code(
                connection_node.identificatieknooppuntofverbinding,
                self.connection_nodes,
                "Connection node",
            )
            self.add_connection_node(connection_node)

        self.add_cross_section(get_hydx_default_profile())
        for hydx_profile in hydx.profiles:
            check_if_element_is_created_with_same_code(
                hydx_profile.identificatieprofieldefinitie,
                self.cross_sections,
                "Profile",
            )
            self.add_cross_section(hydx_profile)

        for connection in hydx.connections:
            check_if_element_is_created_with_same_code(
                connection.identificatieknooppuntofverbinding,
                self.connections,
                "Connection",
            )

            if connection.typeverbinding in ["GSL", "OPL", "ITR", "DRL"]:
                if connection.identificatieprofieldefinitie is None:
                    logger.error(
                        "Verbinding %r has no profile defined",
                        connection.identificatieknooppuntofverbinding,
                    )
                else:
                    linkedprofile = self.find_cross_section(
                        connection.identificatieprofieldefinitie
                    )
                    if linkedprofile is None:
                        logger.error(
                            "Profile %r does not exist for verbinding %r",
                            connection.identificatieprofieldefinitie,
                            connection.identificatieknooppuntofverbinding,
                        )
                        material = None
                    else:
                        material = linkedprofile["material"]
                        profile_is_closed = is_closed(linkedprofile)
                        if profile_is_closed is not None:
                            if connection.typeverbinding == "OPL" and is_closed(
                                linkedprofile
                            ):
                                try:
                                    make_open(linkedprofile)
                                except ValueError:
                                    logger.error(
                                        "Verbinding %r is open (OPL) but uses a closed profiel (%r)",
                                        connection.identificatieknooppuntofverbinding,
                                        connection.identificatieprofieldefinitie,
                                    )
                            elif connection.typeverbinding != "OPL" and not is_closed(
                                linkedprofile
                            ):
                                logger.error(
                                    "Verbinding %r is closed but uses an open profiel (%r)",
                                    connection.identificatieknooppuntofverbinding,
                                    connection.identificatieprofieldefinitie,
                                )

            if connection.typeverbinding in ["GSL", "OPL", "ITR"]:
                self.add_pipe(connection, material)
            elif connection.typeverbinding in ["PMP", "OVS", "DRL"]:
                linkedstructures = [
                    structure
                    for structure in hydx.structures
                    if structure.identificatieknooppuntofverbinding
                    == connection.identificatieknooppuntofverbinding
                ]

                if len(linkedstructures) > 1:
                    logger.error(
                        "Only first structure information is used to create a structure for connection %r",
                        connection.identificatieknooppuntofverbinding,
                    )

                if len(linkedstructures) == 0:
                    logger.error(
                        "Structure does not exist for connection %r",
                        connection.identificatieknooppuntofverbinding,
                    )
                else:
                    self.add_structure(connection, linkedstructures[0])
            else:
                logger.error(
                    'The following "typeverbinding" is not recognized by 3Di exporter: %s',
                    connection.typeverbinding,
                )

        surface_nr = 1
        for surface in hydx.surfaces:
            self.add_impervious_surface_from_surface(surface, surface_nr)
            surface_nr = surface_nr + 1

        for discharge in hydx.discharges:
            linkedvariations = None
            linkedvariations = [
                variation
                for variation in hydx.variations
                if variation.verloopidentificatie == discharge.verloopidentificatie
            ]
            if len(linkedvariations) == 0 and discharge.afvoerendoppervlak is None:
                logger.error(
                    "The following discharge object misses information to be used by 3Di exporter: %s",
                    discharge.identificatieknooppuntofverbinding,
                )
            else:
                self.add_impervious_surface_from_discharge(
                    discharge, surface_nr, linkedvariations
                )
                surface_nr = surface_nr + 1

        for structure in hydx.structures:
            if structure.typekunstwerk == "UIT":
                self.add_1d_boundary(structure)

    def add_connection_node(self, hydx_connection_node):
        """Add hydx.connection_node into threedi.connection_node and threedi.manhole"""

        # get connection_nodes attributes
        lengte = transform_unit_mm_to_m(hydx_connection_node.lengteputbodem)
        breedte = transform_unit_mm_to_m(hydx_connection_node.breedte_diameterputbodem)
        area = determine_area(breedte, lengte)
        connection_node = {
            "code": hydx_connection_node.identificatieknooppuntofverbinding,
            "initial_waterlevel": hydx_connection_node.initielewaterstand,
            "storage_area": round(area, 2),
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
            "width": breedte,
            "length": lengte,
            "shape": get_mapping_value(
                MANHOLE_SHAPE_MAPPING,
                hydx_connection_node.vormput,
                hydx_connection_node.identificatierioolput,
                name_for_logging="manhole shape",
            ),
            "bottom_level": hydx_connection_node.niveaubinnenonderkantput,
            "calculation_type": get_mapping_value(
                CALCULATION_TYPE_MAPPING,
                hydx_connection_node.maaiveldschematisering,
                hydx_connection_node.identificatierioolput,
                name_for_logging="manhole surface schematization",
            ),
            "manhole_indicator": get_mapping_value(
                MANHOLE_INDICATOR_MAPPING,
                hydx_connection_node.typeknooppunt,
                hydx_connection_node.identificatierioolput,
                name_for_logging="manhole indicator",
            ),
        }

        self.manholes.append(manhole)

    def add_pipe(self, hydx_connection, material):
        self.check_if_nodes_of_connection_exists(hydx_connection)
        combined_display_name_string = self.get_connection_display_names_from_manholes(
            hydx_connection
        )

        pipe = {
            "code": hydx_connection.identificatieknooppuntofverbinding,
            "display_name": combined_display_name_string,
            "start_node.code": hydx_connection.identificatieknooppunt1,
            "end_node.code": hydx_connection.identificatieknooppunt2,
            "cross_section_code": hydx_connection.identificatieprofieldefinitie,
            "invert_level_start_point": hydx_connection.bobknooppunt1,
            "invert_level_end_point": hydx_connection.bobknooppunt2,
            "original_length": hydx_connection.lengteverbinding,
            "material": material,
            "sewerage_type": get_mapping_value(
                SEWERAGE_TYPE_MAPPING,
                hydx_connection.typeinzameling,
                combined_display_name_string,
                name_for_logging="pipe sewer type",
            ),
            "calculation_type": 1,
        }
        self.pipes.append(pipe)

    def add_structure(self, hydx_connection, hydx_structure):
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
            self.add_orifice(
                hydx_connection,
                hydx_structure,
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
            "capacity": transform_capacity_to_ls(hydx_structure.pompcapaciteit),
            "sewerage": True,
        }
        self.pumpstations.append(pumpstation)

    def add_weir(self, hydx_connection, hydx_structure, combined_display_name_string):
        waterlevel_boundary = getattr(hydx_structure, "buitenwaterstand", None)
        if waterlevel_boundary is not None:
            timeseries = "0,{0}\n9999,{0}".format(waterlevel_boundary)
            boundary = {
                "node.code": hydx_connection.identificatieknooppunt2,
                "timeseries": timeseries,
                "boundary_type": BoundaryType.WATERLEVEL.value,
            }
            self.outlets.append(boundary)
        else:
            timeseries = None

        hydx_connection = self.get_discharge_coefficients(
            hydx_connection, hydx_structure
        )

        profile = {
            "code": f"weir_{hydx_connection.identificatieknooppuntofverbinding}",
            "shape": CrossSectionShape.RECTANGLE.value,
            "width": hydx_structure.breedteoverstortdrempel,
            "height": None,
        }
        self.cross_sections.append(profile)

        weir = {
            "code": hydx_connection.identificatieknooppuntofverbinding,
            "display_name": combined_display_name_string,
            "start_node.code": hydx_connection.identificatieknooppunt1,
            "end_node.code": hydx_connection.identificatieknooppunt2,
            "cross_section_code": profile["code"],
            "crest_type": CrestType.SHORT_CRESTED.value,
            "crest_level": hydx_structure.niveauoverstortdrempel,
            "discharge_coefficient_positive": hydx_connection.discharge_coefficient_positive,
            "discharge_coefficient_negative": hydx_connection.discharge_coefficient_negative,
            "sewerage": True,
        }
        self.weirs.append(weir)

    def add_orifice(
        self,
        hydx_connection,
        hydx_structure,
        combined_display_name_string,
    ):
        hydx_connection = self.get_discharge_coefficients(
            hydx_connection, hydx_structure
        )
        orifice = {
            "code": hydx_connection.identificatieknooppuntofverbinding,
            "display_name": combined_display_name_string,
            "start_node.code": hydx_connection.identificatieknooppunt1,
            "end_node.code": hydx_connection.identificatieknooppunt2,
            "cross_section_code": hydx_connection.identificatieprofieldefinitie,
            "discharge_coefficient_positive": hydx_connection.discharge_coefficient_positive,
            "discharge_coefficient_negative": hydx_connection.discharge_coefficient_negative,
            "sewerage": True,
            "crest_type": CrestType.SHORT_CRESTED.value,
            "crest_level": hydx_structure.niveaubinnenonderkantprofiel,
        }

        self.orifices.append(orifice)

    def add_cross_section(self, hydx_profile):
        self.cross_sections.append(
            get_cross_section_details(
                hydx_profile,
                record_code=hydx_profile.identificatieprofieldefinitie,
                name_for_logging="profile",
            )
        )

    def find_cross_section(self, identificatieprofieldefinitie):
        code = identificatieprofieldefinitie or "DEFAULT"
        for profile in self.cross_sections:
            if profile["code"] == code:
                return profile

    def add_impervious_surface_from_surface(self, hydx_surface, surface_nr):
        surface = {
            "code": str(surface_nr),
            "display_name": hydx_surface.identificatieknooppuntofverbinding,
            "area": hydx_surface.afvoerendoppervlak,
            "surface_class": get_mapping_value(
                SURFACE_CLASS_MAPPING,
                hydx_surface.afvoerkenmerken.split("_")[0],
                hydx_surface.identificatieknooppuntofverbinding,
                name_for_logging="surface class",
            ),
            "surface_inclination": get_mapping_value(
                SURFACE_INCLINATION_MAPPING,
                hydx_surface.afvoerkenmerken.split("_")[1],
                hydx_surface.identificatieknooppuntofverbinding,
                name_for_logging="surface inclination",
            ),
        }

        self.append_and_map_surface(
            surface, hydx_surface.identificatieknooppuntofverbinding, surface_nr
        )

    def add_impervious_surface_from_discharge(
        self, hydx_discharge, surface_nr, linkedvariations
    ):
        # aanname dat dit altijd gesloten verharding vlak is (niet duidelijk in handleiding)
        # aanname max voor dwf? of average?
        if len(linkedvariations) > 0:
            dwf = max([variation.verloopvolume for variation in linkedvariations])
        else:
            dwf = 0

        if hydx_discharge.afvoerendoppervlak:
            area = hydx_discharge.afvoerendoppervlak
        else:
            area = 0

        surface = {
            "code": str(surface_nr),
            "display_name": hydx_discharge.identificatieknooppuntofverbinding,
            "area": area,
            "surface_class": "gesloten verharding",
            "surface_inclination": "vlak",
            "dry_weather_flow": float(dwf) * 1000,
            "nr_of_inhabitants": hydx_discharge.afvoereenheden,
        }
        self.append_and_map_surface(
            surface, hydx_discharge.identificatieknooppuntofverbinding, surface_nr
        )

    def add_1d_boundary(self, hydx_structure):
        waterlevel_boundary = getattr(hydx_structure, "buitenwaterstand", None)
        if waterlevel_boundary is not None:
            timeseries = "0,{0}\n9999,{0}".format(waterlevel_boundary)
            boundary = {
                "node.code": hydx_structure.identificatieknooppuntofverbinding,
                "timeseries": timeseries,
                "boundary_type": BoundaryType.WATERLEVEL.value,
            }
            self.outlets.append(boundary)

    def append_and_map_surface(
        self, surface, manhole_or_line_id, surface_nr, node_code=None
    ):
        manhole_codes = [manhole["code"] for manhole in self.manholes]
        if manhole_or_line_id in manhole_codes:
            node_code = manhole_or_line_id
        if node_code is None:
            for pipe in self.pipes:
                if manhole_or_line_id == pipe["code"]:
                    node_code = pipe["start_node.code"]
                    break

        if node_code is None:
            logger.error(
                "Connection node %r could not be found for surface %r",
                manhole_or_line_id,
                surface["code"],
            )
            self.impervious_surfaces.append(surface)
            return

        surface_map = {
            "node.code": node_code,
            "imp_surface.code": str(surface_nr),
            "percentage": 100,
        }

        self.impervious_surfaces.append(surface)
        self.impervious_surface_maps.append(surface_map)

    def check_if_nodes_of_connection_exists(self, connection):
        connection_code = connection.identificatieknooppuntofverbinding
        code1 = connection.identificatieknooppunt1
        code2 = connection.identificatieknooppunt2

        manh_list = [manhole["code"] for manhole in self.manholes]
        if code1 is not None and code1 not in manh_list:
            logger.error(
                "Start connection node %r could not be found for record %r",
                code1,
                connection_code,
            )
        elif code2 is not None and code2 not in manh_list:
            logger.error(
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
            logger.error(
                'Flow direction is not recognized for %r with record %r, "OPN" is assumed',
                hydx_connection.typeverbinding,
                hydx_connection.identificatieknooppuntofverbinding,
            )
        if hydx_connection.stromingsrichting == "GSL":
            hydx_connection.discharge_coefficient_positive = 0
            hydx_connection.discharge_coefficient_negative = 0
        elif hydx_connection.stromingsrichting == "OPN":
            hydx_connection.discharge_coefficient_positive = (
                hydx_structure.contractiecoefficientdoorlaatprofiel
                or hydx_structure.afvoercoefficientoverstortdrempel
                or get_mapping_value(
                    DISCHARGE_COEFFICIENT_MAPPING,
                    hydx_structure.typekunstwerk,
                    hydx_structure.identificatieknooppuntofverbinding,
                    name_for_logging="discharge coefficient",
                )
            )
            hydx_connection.discharge_coefficient_negative = (
                hydx_structure.contractiecoefficientdoorlaatprofiel
                or hydx_structure.afvoercoefficientoverstortdrempel
                or get_mapping_value(
                    DISCHARGE_COEFFICIENT_MAPPING,
                    hydx_structure.typekunstwerk,
                    hydx_structure.identificatieknooppuntofverbinding,
                    name_for_logging="discharge coefficient",
                )
            )
        elif hydx_connection.stromingsrichting == "1_2":
            hydx_connection.discharge_coefficient_negative = 0
            hydx_connection.discharge_coefficient_positive = (
                hydx_structure.contractiecoefficientdoorlaatprofiel
                or hydx_structure.afvoercoefficientoverstortdrempel
                or get_mapping_value(
                    DISCHARGE_COEFFICIENT_MAPPING,
                    hydx_structure.typekunstwerk,
                    hydx_structure.identificatieknooppuntofverbinding,
                    name_for_logging="discharge coefficient",
                )
            )
        elif hydx_connection.stromingsrichting == "2_1":
            hydx_connection.discharge_coefficient_positive = 0
            hydx_connection.discharge_coefficient_negative = (
                hydx_structure.contractiecoefficientdoorlaatprofiel
                or hydx_structure.afvoercoefficientoverstortdrempel
                or get_mapping_value(
                    DISCHARGE_COEFFICIENT_MAPPING,
                    hydx_structure.typekunstwerk,
                    hydx_structure.identificatieknooppuntofverbinding,
                    name_for_logging="discharge coefficient",
                )
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
            ("TAB_BRE", ""),
            ("TAB_HGT", ""),
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


def transform_capacity_to_ls(capacity):
    if capacity is not None:
        return round(float(capacity) / 3.6, 5)
    else:
        return None


def transform_unit_mm_to_m(value_mm):
    if value_mm is not None:
        return float(value_mm) / float(1000)
    else:
        return None


def determine_area(width, height):
    if width and height:
        return width * height
    elif width:
        return width * width
    elif height:
        return height * height
    else:
        return 0
