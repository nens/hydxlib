# -*- coding: utf-8 -*-
import json
import logging
from functools import lru_cache

from pyproj import Transformer
from pyproj.crs import CRS
from sqlalchemy import text
from sqlalchemy.orm import load_only
from geoalchemy2.functions import ST_AsText, ST_MakeLine
from threedi_schema import ThreediDatabase
from threedi_schema.domain.models import (
    BoundaryCondition1D,
    ConnectionNode,
    ImperviousSurface,
    ImperviousSurfaceMap,
    Orifice,
    Pipe,
    Pump,
    PumpMap,
    Weir,
)

from .threedi import Threedi

SOURCE_EPSG = 28992
TARGET_EPSG = 4326


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


def to_ewkt(x, y, srid):
    return "srid={};POINT ({} {})".format(srid, x, y)


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
        x, y = transform(x, y, source_epsg, TARGET_EPSG)
        connection_node_list.append(
            ConnectionNode(
                code=connection_node["code"],
                storage_area=connection_node["storage_area"],
                geom=to_ewkt(x, y, TARGET_EPSG),
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
    connection_node_dict = {m.code: m.id for m in connection_node_list}


    pipe_list = []
    for pipe in threedi.pipes:
        pipe = get_start_and_end_connection_node(pipe, connection_node_dict)
        pipe = get_cross_section_fields(pipe, cross_section_dict)
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
        del pump["start_node.code"]
        del pump["end_node.code"]
        connection_node_start_id = pump["connection_node_start_id"]
        connection_node_end_id = pump["connection_node_end_id"]
        pump["connection_node_id"] = connection_node_start_id
        del pump["connection_node_start_id"]
        del pump["connection_node_end_id"]
        pump_object = Pump(**pump)
        pump_list.append(pump_object)
        # without flushing and refreshing at this point there is no pump id to reference in pump_map
        session.add(pump_object)
        session.flush()
        session.refresh()

        pump_map_geom = session.query(
            ST_AsText(ST_MakeLine(ConnectionNode.geom))
        ).filter(
            ConnectionNode.id.in_([connection_node_start_id, connection_node_end_id])
        ).scalar()
        pump_map_list.append(
            PumpMap(
                pump_id=pump_object.id,
                connection_node_id_end=connection_node_end_id,
                geom=pump_map_geom,
                code=pump["code"],
                display_name=pump["display_name"],
            )
        )

        commit_counts["pumps"] += 1

    session.bulk_save_objects(pump_map_list)
    session.commit()

    weir_list = []
    for weir in threedi.weirs:
        weir = get_start_and_end_connection_node(weir, connection_node_dict)
        weir = get_cross_section_fields(weir, cross_section_dict)

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
            outlet["connection_node_id"] = connection_node_dict[outlet["node.code"]]
        else:
            outlet["connection_node_id"] = None
            logger.error("Node of outlet not found in connection nodes")
        del outlet["node.code"]
        outlet_list.append(BoundaryCondition1D(**outlet))

    commit_counts["outlets"] = len(outlet_list)
    session.bulk_save_objects(outlet_list)
    session.commit()

    # Impervious surfaces
    imp_list = []
    for imp in threedi.impervious_surfaces:
        imp_list.append(ImperviousSurface(**imp))
    commit_counts["impervious_surfaces"] = len(imp_list)
    session.bulk_save_objects(imp_list)
    session.commit()

    imp_list = (
        session.query(ImperviousSurface)
        .options(load_only(ImperviousSurface.id, ImperviousSurface.code))
        .order_by(ImperviousSurface.id)
        .all()
    )
    imp_dict = {m.code: m.id for m in imp_list}

    map_list = []
    for imp_map in threedi.impervious_surface_maps:
        imp_map["impervious_surface_id"] = imp_dict[imp_map["imp_surface.code"]]
        imp_map["connection_node_id"] = connection_node_dict[imp_map["node.code"]]
        del imp_map["node.code"]
        del imp_map["imp_surface.code"]
        map_list.append(ImperviousSurfaceMap(**imp_map))
    session.bulk_save_objects(map_list)
    session.commit()

    return commit_counts


def get_start_and_end_connection_node(connection, connection_node_dict):
    if connection["start_node.code"] in connection_node_dict:
        connection["connection_node_start_id"] = connection_node_dict[
            connection["start_node.code"]
        ]
    else:
        connection["connection_node_start_id"] = None
        logger.error(
            "Start node of connection %r not found in connection nodes",
            connection["code"],
        )

    if connection["end_node.code"] in connection_node_dict:
        connection["connection_node_end_id"] = connection_node_dict[
            connection["end_node.code"]
        ]
    else:
        connection["connection_node_end_id"] = None
        logger.error(
            "End node of connection %r not found in connection nodes",
            connection["code"],
        )
    return connection


def get_cross_section_fields(connection, cross_section_dict):
    if connection["cross_section_code"] in cross_section_dict:
        profile = cross_section_dict[
            connection["cross_section_code"]
        ]
        connection["cross_section_shape"] = profile["shape"]
        connection["cross_section_width"] = profile["width"]
        connection["cross_section_height"] = profile["height"]
    else:
        logger.error(
            "Cross section definition of connection %r is not found in cross section definitions",
            connection["code"],
        )

    return connection


def export_json(hydx, path):
    threedi = Threedi()
    threedi.import_hydx(hydx)
    with open(path, "w") as f:
        json.dump(threedi.__dict__, f)
