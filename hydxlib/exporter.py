# -*- coding: utf-8 -*-

import logging
import math
from functools import lru_cache

from geoalchemy2.shape import to_shape
from pyproj import Transformer
from pyproj.crs import CRS
from sqlalchemy import func
from sqlalchemy.orm import load_only
from threedi_schema import ThreediDatabase
from threedi_schema.application.errors import (
    InvalidSRIDException,
    MigrationMissingError,
)
from threedi_schema.domain.models import (
    BoundaryCondition1D,
    ConnectionNode,
    DryWeatherFlow,
    DryWeatherFlowMap,
    Orifice,
    Pipe,
    Pump,
    PumpMap,
    Surface,
    SurfaceMap,
    Weir,
)

from .threedi import Threedi

logger = logging.getLogger(__name__)


# Constructing a Transformer takes quite long, so we use caching here. The
# function is deterministic so this doesn't have any side effects.
@lru_cache(maxsize=1)
def get_transformer(source_epsg, target_epsg):
    return Transformer.from_crs(
        CRS.from_epsg(source_epsg), CRS.from_epsg(target_epsg), always_xy=True
    )


def transform(x, y, source_epsg, target_epsg):
    return get_transformer(source_epsg, target_epsg).transform(x, y)


def to_ewkt_point(x, y, srid):
    return "srid={};POINT ({} {})".format(srid, x, y)


def to_ewkt_linestring(coordinates: tuple[tuple[int, int]], srid: int):
    "coordinates should be passed in as ((x1, y1), (x2, y2))"
    coordinates_string = ", ".join((f"{coord[0]} {coord[1]}") for coord in coordinates)
    return f"SRID={srid};LINESTRING ({coordinates_string})"


def quote_nullable(x):
    if x is None:
        return "NULL"
    else:
        return f"'{x}'"


def export_threedi(hydx, threedi_db_settings):
    threedi = Threedi()
    threedi.import_hydx(hydx)
    commit_counts = write_threedi_to_db(threedi, threedi_db_settings)
    logger.info("GWSW-hydx exchange created elements: %r", commit_counts)
    return threedi


def write_threedi_to_db(threedi, threedi_db_settings):
    """
    writes threedi to model database

    threedi (dict): dictionary with for each object type a list of objects

    returns: (dict) with number of objects committed to the database of
             each object type

    """

    commit_counts = {}

    if isinstance(threedi_db_settings, dict):
        path = threedi_db_settings["db_file"]
    else:
        path = threedi_db_settings

    db = ThreediDatabase(path)
    schema = db.schema
    try:
        schema.validate_schema
    except MigrationMissingError:
        logger.error("Cannot export hydx to outdated schematisation")
        return
    try:
        target_epsg = (
            schema.epsg_code if schema.epsg_code is not None else schema._get_dem_epsg()
        )
    except InvalidSRIDException:
        logger.error("Cannot find a valid EPSG code for the schema.")
        return
    session = db.get_session()
    cross_section_dict = {}
    for profile in threedi.cross_sections:
        cross_section_dict[profile["code"]] = {
            "width": profile["width"],
            "height": profile["height"],
            "shape": profile["shape"],
        }

    connection_node_list = []
    for connection_node in threedi.connection_nodes:
        x, y, source_epsg = connection_node["geom"]
        x, y = transform(x, y, source_epsg, target_epsg)
        connection_node_list.append(
            ConnectionNode(
                display_name=connection_node["display_name"],
                code=connection_node["code"],
                storage_area=connection_node["storage_area"],
                geom=to_ewkt_point(x, y, target_epsg),
                bottom_level=connection_node["bottom_level"],
                manhole_surface_level=connection_node["manhole_surface_level"],
                exchange_type=connection_node["exchange_type"],
                visualisation=connection_node["visualisation"],
            )
        )

    commit_counts["connection_nodes"] = len(connection_node_list)
    session.bulk_save_objects(connection_node_list)
    session.commit()

    connection_node_list = (
        session.query(ConnectionNode)
        .options(load_only(ConnectionNode.id, ConnectionNode.code))
        .order_by(ConnectionNode.id)
        .all()
    )
    connection_node_dict = {
        m.code: {"id": m.id, "geom": m.geom} for m in connection_node_list
    }
    pipe_list = []
    for pipe in threedi.pipes:
        pipe = get_start_and_end_connection_node(pipe, connection_node_dict)
        pipe = get_cross_section_fields(pipe, cross_section_dict)
        pipe = get_line_between_nodes(
            pipe, connection_node_dict, "start_node.code", "end_node.code", target_epsg
        )
        # Skip creating object without geometry; error handling is handled by the functions above
        if pipe["geom"] is None:
            continue
        del pipe["start_node.code"]
        del pipe["end_node.code"]
        del pipe["cross_section_code"]
        pipe_list.append(Pipe(**pipe))
    commit_counts["pipes"] = len(pipe_list)
    session.bulk_save_objects(pipe_list)
    session.commit()

    pump_list = []
    pump_map_list = []
    commit_counts["pumps"] = 0
    for pump in threedi.pumps:
        pump = get_start_and_end_connection_node(pump, connection_node_dict)
        # breakpoint()
        pump["connection_node_id"] = pump["connection_node_id_start"]
        # skip if no connection node is linked
        if pump["connection_node_id"] is None:
            continue
        pump["geom"] = get_node_geom(pump, connection_node_dict, "start_node.code")
        connection_node_id_start = pump.pop("connection_node_id_start")
        connection_node_id_end = pump.pop("connection_node_id_end")
        if connection_node_id_start is not None and (
            connection_node_id_start == connection_node_id_end
        ):
            logger.error(
                f"Pump {pump['code']} will be skipped because it has same start and end node"
            )
            continue
        del pump["start_node.code"]
        del pump["end_node.code"]
        pump_object = Pump(**pump)
        pump_list.append(pump_object)
        # without flushing and refreshing at this point there is no pump id to reference in pump_map
        session.add(pump_object)
        session.flush()
        session.refresh(pump_object)

        if connection_node_id_start is not None and connection_node_id_end is not None:
            pump_map_geom = (
                session.query(func.ST_AsText(func.MakeLine(ConnectionNode.geom)))
                .filter(
                    ConnectionNode.id.in_(
                        [connection_node_id_start, connection_node_id_end]
                    )
                )
                .scalar()
            )
            pump_map_list.append(
                PumpMap(
                    pump_id=pump_object.id,
                    connection_node_id_end=connection_node_id_end,
                    geom=pump_map_geom,
                    code=pump["code"],
                    display_name=pump["display_name"],
                )
            )

        commit_counts["pumps"] += 1

    if len(pump_map_list) > 0:
        session.bulk_save_objects(pump_map_list)
    session.commit()

    weir_list = []
    for weir in threedi.weirs:
        weir = get_start_and_end_connection_node(weir, connection_node_dict)
        weir = get_cross_section_fields(weir, cross_section_dict)
        weir = get_line_between_nodes(
            weir, connection_node_dict, "start_node.code", "end_node.code", target_epsg
        )
        if weir["geom"] is None:
            continue
        del weir["start_node.code"]
        del weir["end_node.code"]
        del weir["cross_section_code"]
        weir_list.append(Weir(**weir))
    commit_counts["weirs"] = len(weir_list)
    session.bulk_save_objects(weir_list)
    session.commit()

    orifice_list = []
    for orifice in threedi.orifices:
        orifice = get_start_and_end_connection_node(orifice, connection_node_dict)
        orifice = get_cross_section_fields(orifice, cross_section_dict)
        orifice = get_line_between_nodes(
            orifice,
            connection_node_dict,
            "start_node.code",
            "end_node.code",
            target_epsg,
        )
        if orifice["geom"] is None:
            continue
        del orifice["start_node.code"]
        del orifice["end_node.code"]
        del orifice["cross_section_code"]
        orifice_list.append(Orifice(**orifice))
    commit_counts["orifices"] = len(orifice_list)
    session.bulk_save_objects(orifice_list)
    session.commit()

    # Outlets (must be saved after weirs, orifice, pumpstation, etc.
    # because of constraints) TO DO: bounds aan meerdere leidingen overslaan
    outlet_list = []
    for outlet in threedi.outlets:
        if outlet["node.code"] in connection_node_dict:
            outlet["connection_node_id"] = connection_node_dict[outlet["node.code"]][
                "id"
            ]
            outlet["geom"] = get_node_geom(outlet, connection_node_dict, "node.code")
        else:
            outlet["connection_node_id"] = None
            logger.error("Node of outlet not found in connection nodes")
            continue
        del outlet["node.code"]
        outlet["time_units"] = "minutes"
        outlet["interpolate"] = 1
        outlet_list.append(BoundaryCondition1D(**outlet))

    commit_counts["outlets"] = len(outlet_list)
    session.bulk_save_objects(outlet_list)
    session.commit()

    # 0d inflow
    surf_list = []
    dwf_list = []
    for surface in threedi.impervious_surfaces:
        surface["surface_parameters_id"] = get_surface_parameters_id(
            surface_class=surface.pop("surface_class", None),
            surface_inclination=surface.pop("surface_inclination", None),
        )
        if surface["surface_parameters_id"] is None:
            logger.error("surface parameter id not found for surface")
        connection_node = connection_node_dict.get(surface["node.code"], None)
        if connection_node is None:
            logger.error(f"node not found for surface {surface['code']}")
        node_geom = connection_node["geom"]
        if surface["area"] > 0:
            side_length = math.sqrt(surface["area"])
            node_x = session.query(func.ST_X(node_geom)).scalar()
            node_y = session.query(func.ST_Y(node_geom)).scalar()
            surface[
                "geom"
            ] = f"""
                srid={target_epsg};POLYGON(({node_x - side_length / 2} {node_y - side_length / 2},
                         {node_x + side_length / 2} {node_y - side_length / 2},
                         {node_x + side_length / 2} {node_y + side_length / 2},
                         {node_x - side_length / 2} {node_y + side_length / 2},
                         {node_x - side_length / 2} {node_y - side_length / 2}
                         ))"""
        dwf = {
            "code": surface["code"],
            "display_name": surface["display_name"],
            "daily_total": surface.pop("dry_weather_flow", None),
            "multiplier": surface.pop("nr_of_inhabitants", None),
        }
        dwf["geom"] = (
            session.query(func.ST_AsText(func.ST_Buffer(ConnectionNode.geom, 1)))
            .filter(
                ConnectionNode.id == connection_node_dict[surface["node.code"]]["id"]
            )
            .scalar()
        )
        surface.pop("node.code", None)
        if surface["area"] != 0:
            surf_list.append(Surface(**surface))
        if dwf["daily_total"] is not None and dwf["multiplier"] is not None:
            dwf_list.append(DryWeatherFlow(**dwf))
    commit_counts["surfaces"] = len(surf_list)
    commit_counts["dry_weather_flows"] = len(dwf_list)
    session.bulk_save_objects(surf_list)
    session.bulk_save_objects(dwf_list)
    session.commit()

    for obj_name, obj, map_obj in [
        ("surface", Surface, SurfaceMap),
        ("dry_weather_flow", DryWeatherFlow, DryWeatherFlowMap),
    ]:
        obj_list = (
            session.query(obj)
            .options(load_only(obj.id, obj.code))
            .order_by(obj.id)
            .all()
        )
        obj_map = {m.code: m.id for m in obj_list}
        map_list = []
        for imp_map in threedi.impervious_surface_maps:
            import copy

            item = copy.copy(imp_map)
            if not item["imp_surface.code"] in obj_map:
                continue
            item[f"{obj_name}_id"] = obj_map[item["imp_surface.code"]]
            item["connection_node_id"] = connection_node_dict[item["node.code"]]["id"]
            node_geom = connection_node_dict[item["node.code"]]["geom"]
            node_x = session.query(func.ST_X(node_geom)).scalar()
            node_y = session.query(func.ST_Y(node_geom)).scalar()
            obj_geom = (
                session.query(func.PointOnSurface(obj.geom))
                .filter(obj.id == item[f"{obj_name}_id"])
                .scalar()
            )
            obj_x = session.query(func.ST_X(obj_geom)).scalar()
            obj_y = session.query(func.ST_Y(obj_geom)).scalar()
            if obj_x == node_x and obj_y == node_y:
                obj_y += 1
            item[
                "geom"
            ] = f"srid={target_epsg};LINESTRING({obj_x} {obj_y}, {node_x} {node_y})"
            del item["node.code"]
            del item["imp_surface.code"]
            map_list.append(map_obj(**item))
        session.bulk_save_objects(map_list)
        session.commit()

    return commit_counts


def get_surface_parameters_id(surface_class, surface_inclination):
    id_map = {
        "gesloten verharding:hellend": 101,
        "gesloten verharding:vlak": 102,
        "gesloten verharding:uitgestrekt": 103,
        "open verharding:hellend": 104,
        "open verharding:vlak": 105,
        "open verharding:uitgestrekt": 106,
        "pand:hellend": 107,
        "pand:vlak": 108,
        "pand:uitgestrekt": 109,
        "onverhard:hellend": 110,
        "onverhard:vlak": 111,
        "onverhard:uitgestrekt": 112,
        "half verhard:hellend": 113,
        "half verhard:vlak": 114,
        "half verhard:uitgestrekt": 115,
    }
    return id_map.get(f"{surface_class}:{surface_inclination}", None)


def get_connection_node(connection, connection_node_dict, node_key):
    if connection[node_key] in connection_node_dict:
        return connection_node_dict[connection[node_key]]["id"]
    else:
        logger.error(
            f"{node_key} of connection {connection['code']} not found in connection nodes",
        )
        return None


def get_start_and_end_connection_node(connection, connection_node_dict):
    connection["connection_node_id_start"] = get_connection_node(
        connection, connection_node_dict, "start_node.code"
    )
    connection["connection_node_id_end"] = get_connection_node(
        connection, connection_node_dict, "end_node.code"
    )
    return connection


def get_cross_section_fields(connection, cross_section_dict):
    if connection["cross_section_code"] in cross_section_dict:
        profile = cross_section_dict[connection["cross_section_code"]]
        connection["cross_section_shape"] = profile["shape"]
        if connection["cross_section_shape"] in (5, 6, 7):
            # tabulated_YZ: width -> Y; height -> Z
            if connection["cross_section_shape"] == 7:
                print("tabulated yz")
                col1 = profile["width"]
                col2 = profile["height"]
            # tabulated_trapezium or tabulated_rectangle: height, width
            else:
                print("tabulated other")
                col1 = profile["height"]
                col2 = profile["width"]
            connection["cross_section_table"] = None
            if isinstance(profile["width"], str) and isinstance(profile["height"], str):
                col1 = col1.split()
                col2 = col2.split()
                if len(col1) == len(col2):
                    connection["cross_section_table"] = "\n".join(
                        [",".join(row) for row in zip(col1, col2)]
                    )
        elif profile["shape"] is not None:
            connection["cross_section_width"] = profile["width"]
            connection["cross_section_height"] = profile["height"]
    else:
        logger.error(
            "Cross section definition of connection %r is not found in cross section definitions",
            connection["code"],
        )

    return connection


def get_node_geom(connection, connection_node_dict, node_key):
    node_id = connection[node_key]
    if node_id in connection_node_dict:
        return connection_node_dict[node_id]["geom"]
    else:
        logger.error(
            f'Node {node_key} of connection {connection["code"]} not found in connection nodes'
        )
        return None


def get_line_between_nodes(
    connection, connection_node_dict, start_key, end_key, target_epsg
):
    start_node_geom = get_node_geom(connection, connection_node_dict, start_key)
    end_node_geom = get_node_geom(connection, connection_node_dict, end_key)
    if start_node_geom and end_node_geom:
        start_node_geom = to_shape(start_node_geom)
        end_node_geom = to_shape(end_node_geom)
        geom = to_ewkt_linestring(
            coordinates=(
                (start_node_geom.x, start_node_geom.y),
                (end_node_geom.x, end_node_geom.y),
            ),
            srid=target_epsg,
        )
    else:
        logger.error(
            f'Cannot calculate geom for connection {connection["code"]} without start and end node'
        )
        geom = None
    connection["geom"] = geom
    return connection
