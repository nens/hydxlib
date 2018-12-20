# -*- coding: utf-8 -*-
import logging

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


def export_hydx(hydxdict, csvfile):
    pass


def export_threedi(hydx, threedi_db_settings):
    threedi = Threedi()
    threedi.import_hydx(hydx)
    commit_counts = write_threedi_to_db(threedi, threedi_db_settings)
    print(commit_counts)

    return threedi


def write_threedi_to_db(threedi, threedi_db_settings):
    """
        writes threedi to model database

        threedi (dict): dictionary with for each object type a list of objects

        returns: (dict) with number of objects committed to the database of
                 each object type

        """

    commit_counts = {}

    # TODO temporarily db setup!
    print(threedi_db_settings)
    db = ThreediDatabase(
        {
            "host": threedi_db_settings['threedi_host'],
            "port": threedi_db_settings['threedi_port'],
            "database": threedi_db_settings['threedi_dbname'],
            "username": threedi_db_settings['threedi_user'],
            "password": threedi_db_settings['threedi_password'],
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
    # crs_list = []
    # for crs in threedi['profiles'].values():
    #     crs_list.append(CrossSectionDefinition(**crs))

    # commit_counts['profiles'] = len(crs_list)
    # session.bulk_save_objects(crs_list)
    # session.commit()

    # crs_list = session.query(CrossSectionDefinition).options(
    #     load_only("id", "code")).order_by(CrossSectionDefinition.id).all()
    # crs_dict = {m.code: m.id for m in crs_list}
    # del crs_list

    con_list = []
    srid = 28992

    for connection_node in threedi.connection_nodes:
        wkt = "POINT({0} {1})".format(*connection_node["geom"])
        con_list.append(
            ConnectionNode(
                code=connection_node["code"],
                storage_area=None,
                the_geom="srid={0};{1}".format(srid, wkt),
            )
        )

    commit_counts["connection_nodes"] = len(con_list)
    session.bulk_save_objects(con_list)
    session.commit()

    # con_list = session.query(ConnectionNode).options(
    #     load_only("id", "code")).order_by(ConnectionNode.id).all()
    # con_dict = {m.code: m.id for m in con_list}
    # del con_list

    # # add extra references for link nodes (one node, multiple linked codes
    # for link in threedi['links']:
    #     try:
    #         if link['end_node.code'] in con_dict:
    #             con_dict[link['end_node.code']
    #                      ] = con_dict[link['start_node.code']]
    #         else:
    #             con_dict[link['end_node.code']
    #                      ] = con_dict[link['start_node.code']]
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

    # con_dict[None] = None
    # con_dict[''] = None

    # man_list = []
    # for manhole in threedi['manholes']:
    #     del manhole['geom']
    #     del manhole['storage_area']

    #     manhole['connection_node_id'] = con_dict[manhole['code']]
    #     man_list.append(Manhole(**manhole))

    # commit_counts['manholes'] = len(man_list)
    # session.bulk_save_objects(man_list)
    # session.commit()
    # del man_list

    # pipe_list = []
    # for pipe in threedi['pipes']:
    #     try:
    #         pipe['connection_node_start_id'] = con_dict[
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
    #         pipe['connection_node_end_id'] = con_dict[
    #             pipe['end_node.code']]
    #     except KeyError:
    #         self.log.add(
    #             logging.ERROR,
    #             'End node of pipe not found in nodes',
    #             {},
    #             'End node {end_node} of pipe with code {code} not found',
    #             {'end_node': pipe['end_node.code'], 'code': pipe['code']}
    #         )

    #     pipe['cross_section_definition_id'] = crs_dict[pipe['crs_code']]

    #     del pipe['start_node.code']
    #     del pipe['end_node.code']
    #     del pipe['crs_code']
    #     del pipe['cross_section_details']

    #     pipe_list.append(Pipe(**pipe))

    # commit_counts['pipes'] = len(pipe_list)
    # session.bulk_save_objects(pipe_list)
    # session.commit()
    # del pipe_list

    # obj_list = []
    # for pump in threedi['pumpstations']:
    #     try:
    #         pump['connection_node_start_id'] = con_dict[
    #             pump['start_node.code']]
    #     except KeyError:
    #         self.log.add(
    #             logging.ERROR,
    #             'Start node of pump not found in nodes',
    #             {},
    #             'Start node {start_node} of pump with code {code} not '
    #             'found',
    #             {'start_node': pump['start_node.code'],
    #                 'code': pump['code']}
    #         )

    #     try:
    #         pump['connection_node_end_id'] = con_dict[
    #             pump['end_node.code']]
    #     except KeyError:
    #         self.log.add(
    #             logging.ERROR,
    #             'End node of pump not found in nodes',
    #             {},
    #             'End node {end_node} of pump with code {code} not found',
    #             {'end_node': pump['end_node.code'], 'code': pump['code']}
    #         )

    #     del pump['start_node.code']
    #     del pump['end_node.code']

    #     obj_list.append(Pumpstation(**pump))

    # for weir in threedi['weirs']:
    #     try:
    #         weir['connection_node_start_id'] = con_dict[
    #             weir['start_node.code']]
    #     except KeyError:
    #         self.log.add(
    #             logging.ERROR,
    #             'Start node of weir not found in nodes',
    #             {},
    #             'Start node {start_node} of weir with code {code} not '
    #             'found',
    #             {'start_node': weir['start_node.code'],
    #                 'code': weir['code']}
    #         )

    #     try:
    #         weir['connection_node_end_id'] = con_dict[
    #             weir['end_node.code']]
    #     except KeyError:
    #         self.log.add(
    #             logging.ERROR,
    #             'End node of weir not found in nodes',
    #             {},
    #             'End node {end_node} of weir with code {code} not found',
    #             {'end_node': weir['end_node.code'], 'code': weir['code']}
    #         )

    #     weir['cross_section_definition_id'] = crs_dict[weir['crs_code']]

    #     del weir['start_node.code']
    #     del weir['end_node.code']
    #     del weir['crs_code']
    #     del weir['cross_section_details']
    #     del weir['boundary_details']

    #     obj_list.append(Weir(**weir))

    # for orif in threedi['orifices']:
    #     try:
    #         orif['connection_node_start_id'] = con_dict[
    #             orif['start_node.code']]
    #     except KeyError:
    #         self.log.add(
    #             logging.ERROR,
    #             'Start node of orifice not found in nodes',
    #             {},
    #             'Start node {start_node} of orifice with code {code} not '
    #             'found',
    #             {'start_node': orif['start_node.code'],
    #                 'code': orif['code']}
    #         )

    #     try:
    #         orif['connection_node_end_id'] = con_dict[
    #             orif['end_node.code']]
    #     except KeyError:
    #         self.log.add(
    #             logging.ERROR,
    #             'End node of orifice not found in nodes',
    #             {},
    #             'End node {end_node} of orifice with code {code} not '
    #             'found',
    #             {'end_node': orif['end_node.code'], 'code': orif['code']}
    #         )

    #     orif['cross_section_definition_id'] = crs_dict[orif['crs_code']]

    #     del orif['start_node.code']
    #     del orif['end_node.code']
    #     del orif['crs_code']
    #     del orif['cross_section_details']

    #     obj_list.append(Orifice(**orif))

    # commit_counts['structures'] = len(obj_list)
    # session.bulk_save_objects(obj_list)
    # session.commit()
    # del obj_list

    # # Outlets (must be saved after weirs, orifice, pumpstation, etc.
    # # because of constraints)
    # outlet_list = []
    # for outlet in threedi['outlets']:
    #     try:
    #         outlet['connection_node_id'] = con_dict[outlet['node.code']]

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
    # del outlet_list

    # # Impervious surfaces
    # imp_list = []
    # for imp in threedi['impervious_surfaces']:
    #     imp_list.append(ImperviousSurface(**imp))

    # commit_counts['impervious_surfaces'] = len(imp_list)
    # session.bulk_save_objects(imp_list)
    # session.commit()

    # imp_list = session.query(ImperviousSurface).options(
    #     load_only("id", "code")).order_by(ImperviousSurface.id).all()
    # imp_dict = {m.code: m.id for m in imp_list}
    # del imp_list

    # map_list = []
    # for imp_map in threedi['impervious_surface_maps']:
    #     try:
    #         imp_map['connection_node_id'] = con_dict[imp_map['node.code']]
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
