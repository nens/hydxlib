# -*- coding: utf-8 -*-
import logging
from sqlalchemy.orm import load_only

from gwswlib.threedi import Threedi
from gwswlib.sql_models.threedi_database import ThreediDatabase
from gwswlib.sql_models.model_schematisation import (
    ConnectionNode,
    Manhole,
    BoundaryCondition1D,
    Pipe,
    CrossSectionDefinition,
    Orifice,
    Weir,
    Pumpstation,
    ImperviousSurface,
    ImperviousSurfaceMap,
)

logger = logging.getLogger(__name__)


def export_threedi(hydx, threedi_db_settings):
    threedi = Threedi()
    threedi.import_hydx(hydx)
    commit_counts = write_threedi_to_db(threedi, threedi_db_settings)
    logger.info("Following elements are created %r", commit_counts)
    return threedi


def write_threedi_to_db(threedi, threedi_db_settings):
    """
        writes threedi to model database

        threedi (dict): dictionary with for each object type a list of objects

        returns: (dict) with number of objects committed to the database of
                 each object type

        """

    commit_counts = {}

    db = ThreediDatabase(
        {
            "host": threedi_db_settings["threedi_host"],
            "port": threedi_db_settings["threedi_port"],
            "database": threedi_db_settings["threedi_dbname"],
            "username": threedi_db_settings["threedi_user"],
            "password": threedi_db_settings["threedi_password"],
        },
        "postgres",
    )

    session = db.get_session()

    # set all autoincrement counters to max ids
    if db.db_type == "postgres":
        for table in (
            ConnectionNode,
            Manhole,
            BoundaryCondition1D,
            Pipe,
            CrossSectionDefinition,
            Orifice,
            Weir,
            Pumpstation,
            ImperviousSurface,
            ImperviousSurfaceMap,
        ):

            session.execute(
                "SELECT setval('{table}_id_seq', max(id)) "
                "FROM {table}".format(table=table.__tablename__)
            )

        session.commit()

    cross_section_list = []
    for cross_section in threedi.cross_sections.values():
        cross_section_list.append(CrossSectionDefinition(**cross_section))

    commit_counts["cross_sections"] = len(cross_section_list)
    session.bulk_save_objects(cross_section_list)
    session.commit()

    cross_section_list = (
        session.query(CrossSectionDefinition)
        .options(load_only("id", "code"))
        .order_by(CrossSectionDefinition.id)
        .all()
    )
    cross_section_dict = {m.code: m.id for m in cross_section_list}

    connection_node_list = []
    srid = 28992

    for connection_node in threedi.connection_nodes:
        wkt = "POINT({0} {1})".format(*connection_node["geom"])
        connection_node_list.append(
            ConnectionNode(
                code=connection_node["code"],
                storage_area=None,
                the_geom="srid={0};{1}".format(srid, wkt),
            )
        )

    commit_counts["connection_nodes"] = len(connection_node_list)
    session.bulk_save_objects(connection_node_list)
    session.commit()

    connection_node_list = (
        session.query(ConnectionNode)
        .options(load_only("id", "code"))
        .order_by(ConnectionNode.id)
        .all()
    )
    connection_node_dict = {m.code: m.id for m in connection_node_list}

    # # add extra references for link nodes (one node, multiple linked codes
    # for link in threedi.links:
    #     try:
    #         if link['end_node.code'] in connection_node_dict:
    #             connection_node_dict[link['end_node.code']
    #                      ] = connection_node_dict[link['start_node.code']]
    #         else:
    #             connection_node_dict[link['end_node.code']
    #                      ] = connection_node_dict[link['start_node.code']]
    #     except KeyError:
    #         self.log.add(
    #             logging.ERROR,
    #             'node of link not found in nodes',
    #             {},
    #             'start node {start_node} or end_node {end_node} of link '
    #             'definition not found',
    #             {'start_node': link['start_node.code'],
    #              'end_node': link['end_node.code']}
    #         )

    # connection_node_dict[None] = None
    # connection_node_dict[''] = None

    man_list = []
    threedi.manholes.reverse()
    for manhole in threedi.manholes:
        unique_values = [m.__dict__["connection_node_id"] for m in man_list]
        manhole["connection_node_id"] = connection_node_dict[manhole["code"]]

        if manhole["connection_node_id"] not in unique_values:
            man_list.append(Manhole(**manhole))
        else:
            logging.error(
                "Manhole with %r could not be created in 3di due to double values in ConnectionNode",
                manhole["code"],
            )

    commit_counts["manholes"] = len(man_list)
    session.bulk_save_objects(man_list)
    session.commit()

    # pipe_list = []
    # for pipe in threedi.pipes:
    #     try:
    #         pipe['connection_node_start_id'] = connection_node_dict[
    #             pipe['start_node.code']]
    #     except KeyError:
    #         self.log.add(
    #             logging.ERROR,
    #             'Start node of pipe not found in nodes',
    #             {},
    #             'Start node {start_node} of pipe with code {code} not '
    #             'found',
    #             {'start_node': pipe['start_node.code'],
    #                 'code': pipe['code']}
    #         )

    #     try:
    #         pipe['connection_node_end_id'] = connection_node_dict[
    #             pipe['end_node.code']]
    #     except KeyError:
    #         self.log.add(
    #             logging.ERROR,
    #             'End node of pipe not found in nodes',
    #             {},
    #             'End node {end_node} of pipe with code {code} not found',
    #             {'end_node': pipe['end_node.code'], 'code': pipe['code']}
    #         )

    #     pipe['cross_section_definition_id'] = cross_section_dict[pipe['cross_section_code']]

    #     del pipe['start_node.code']
    #     del pipe['end_node.code']
    #     del pipe['cross_section_code']
    #     del pipe['cross_section_details']

    #     pipe_list.append(Pipe(**pipe))

    # commit_counts['pipes'] = len(pipe_list)
    # session.bulk_save_objects(pipe_list)
    # session.commit()

    pump_list = []
    for pump in threedi.pumpstations:
        pump = get_start_and_end_connection_node(pump, connection_node_dict)
        del pump["start_node.code"]
        del pump["end_node.code"]
        pump_list.append(Pumpstation(**pump))

    commit_counts["pumpstations"] = len(pump_list)
    session.bulk_save_objects(pump_list)
    session.commit()

    weir_list = []
    for weir in threedi.weirs:
        weir = get_start_and_end_connection_node(weir, connection_node_dict)
        weir = get_cross_section_definition_id(weir, cross_section_dict)

        del weir["start_node.code"]
        del weir["end_node.code"]
        del weir["cross_section_code"]
        del weir["cross_section_details"]
        del weir["boundary_details"]
        weir_list.append(Weir(**weir))

    commit_counts["weirs"] = len(weir_list)
    session.bulk_save_objects(weir_list)
    session.commit()

    orifice_list = []
    for orifice in threedi.orifices:
        orifice = get_start_and_end_connection_node(orifice, connection_node_dict)
        orifice = get_cross_section_definition_id(orifice, cross_section_dict)

        del orifice["start_node.code"]
        del orifice["end_node.code"]
        del orifice["cross_section_code"]
        del orifice["cross_section_details"]

        orifice_list.append(Orifice(**orifice))

    commit_counts["orifices"] = len(orifice_list)
    session.bulk_save_objects(orifice_list)
    session.commit()

    # # Outlets (must be saved after weirs, orifice, pumpstation, etc.
    # # because of constraints)
    # outlet_list = []
    # for outlet in threedi.outlets:
    #     try:
    #         outlet['connection_node_id'] = connection_node_dict[outlet['node.code']]

    #         del outlet['node.code']
    #         outlet_list.append(BoundaryCondition1D(**outlet))
    #     except KeyError:
    #         self.log.add(
    #             logging.ERROR,
    #             'node of outlet not found in nodes',
    #             {},
    #             'node {node} of outlet definition not found',
    #             {'node': outlet['node.code']}
    #         )

    # commit_counts['outlets'] = len(outlet_list)
    # session.bulk_save_objects(outlet_list)
    # session.commit()

    # # Impervious surfaces
    # imp_list = []
    # for imp in threedi.impervious_surfaces:
    #     imp_list.append(ImperviousSurface(**imp))

    # commit_counts['impervious_surfaces'] = len(imp_list)
    # session.bulk_save_objects(imp_list)
    # session.commit()

    # imp_list = session.query(ImperviousSurface).options(
    #     load_only("id", "code")).order_by(ImperviousSurface.id).all()
    # imp_dict = {m.code: m.id for m in imp_list}

    # map_list = []
    # for imp_map in threedi.impervious_surface_maps:
    #     try:
    #         imp_map['connection_node_id'] = connection_node_dict[imp_map['node.code']]
    #     except KeyError:
    #         self.log.add(
    #             logging.ERROR,
    #             'Manhole connected to impervious surface not found',
    #             {},
    #             'Node {node} of impervious surface map connected to '
    #             'impervious surface with code {code} not found',
    #             {'node': imp_map['node.code'],
    #                 'code': imp_map['imp_surface.code']}
    #         )
    #         continue

    #     imp_map['impervious_surface_id'] = imp_dict[
    #         imp_map['imp_surface.code']]
    #     del imp_map['node.code']
    #     del imp_map['imp_surface.code']

    #     map_list.append(ImperviousSurfaceMap(**imp_map))

    # session.bulk_save_objects(map_list)
    # session.commit()

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
        logging.error(
            "End node of connection %r not found in connection nodes",
            connection["code"],
        )
    return connection


def get_cross_section_definition_id(connection, cross_section_dict):
    if connection["cross_section_code"] in cross_section_dict:
        connection["cross_section_definition_id"] = cross_section_dict[
            connection["cross_section_code"]
        ]
    else:
        connection["cross_section_definition_id"] = None
        logger.error(
            "Cross section definition of connection %r is not found in cross section definitions",
            connection["code"],
        )
    return connection
